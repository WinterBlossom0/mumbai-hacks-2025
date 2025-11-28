// Clerk Authentication Module
let clerk = null;
let currentUser = null;
let useClerk = false;

/**
 * Initialize Clerk authentication
 */
async function initializeClerk() {
    console.log('Initializing Clerk authentication...');

    // Wait for Clerk to load
    let attempts = 0;
    while (!window.Clerk && attempts < 50) {
        await new Promise(resolve => setTimeout(resolve, 100));
        attempts++;
    }

    if (!window.Clerk) {
        console.log('Clerk SDK not loaded, using fallback user 0');
        useFallbackAuth();
        return;
    }

    try {
        clerk = window.Clerk;
        await clerk.load();

        console.log('Clerk loaded successfully');

        // Check if user is already signed in
        if (clerk.user) {
            currentUser = clerk.user;
            useClerk = true;
            console.log('✓ User signed in:', currentUser.emailAddresses[0]?.emailAddress);
            updateUIForSignedInUser();
        } else {
            console.log('No user signed in yet');
            updateUIForSignedOutUser();
        }

        setupAuthButtons();

    } catch (error) {
        console.error('Error initializing Clerk:', error);
        useFallbackAuth();
    }
}

/**
 * Setup authentication button event listeners
 */
function setupAuthButtons() {
    const signInBtn = document.getElementById('sign-in-btn');
    const signOutBtn = document.getElementById('sign-out-btn');

    if (signInBtn) {
        signInBtn.addEventListener('click', async () => {
            try {
                console.log('Opening Clerk sign in...');
                await clerk.openSignIn();
            } catch (error) {
                console.error('Error opening sign in:', error);
            }
        });
    }

    if (signOutBtn) {
        signOutBtn.addEventListener('click', async () => {
            try {
                console.log('Signing out...');
                await clerk.signOut();
                currentUser = null;
                useClerk = false;
                updateUIForSignedOutUser();

                // Redirect to home page
                document.querySelector('[data-page="home"]').click();
                console.log('✓ Signed out successfully');
            } catch (error) {
                console.error('Error signing out:', error);
            }
        });
    }
}

/**
 * Update UI when user is signed in
 */
function updateUIForSignedInUser() {
    console.log('Updating UI for signed in user');
    const signedOut = document.getElementById('signed-out');
    const signedIn = document.getElementById('signed-in');
    const userAvatar = document.getElementById('user-avatar');
    const userEmail = document.getElementById('user-email');

    if (signedOut && signedIn) {
        signedOut.style.display = 'none';
        signedIn.style.display = 'flex';
    }

    if (currentUser) {
        // Set user avatar
        const avatarUrl = currentUser.imageUrl || currentUser.profileImageUrl || getDefaultAvatar(currentUser.emailAddresses[0]?.emailAddress);
        if (userAvatar) {
            userAvatar.src = avatarUrl;
            userAvatar.alt = `${currentUser.firstName || 'User'}'s avatar`;
        }

        // Set user email
        const email = currentUser.emailAddresses[0]?.emailAddress ||
            currentUser.primaryEmailAddress?.emailAddress ||
            'Unknown';
        if (userEmail) {
            userEmail.textContent = email;
        }

        console.log('✓ UI updated - Email:', email);
    }
}

/**
 * Update UI when user is signed out
 */
function updateUIForSignedOutUser() {
    console.log('Updating UI for signed out user');
    const signedOut = document.getElementById('signed-out');
    const signedIn = document.getElementById('signed-in');

    if (signedOut && signedIn) {
        signedOut.style.display = 'flex';
        signedIn.style.display = 'none';
    }
}

/**
 * Get current user ID for API requests
 */
function getCurrentUserId() {
    if (useClerk && currentUser && currentUser.id) {
        return currentUser.id;
    }
    return '0'; // Always fall back to user 0
}

/**
 * Get current user email for API requests
 */
function getCurrentUserEmail() {
    if (useClerk && currentUser) {
        return currentUser.emailAddresses[0]?.emailAddress ||
            currentUser.primaryEmailAddress?.emailAddress ||
            'user0@gmail.com';
    }
    return 'user0@gmail.com'; // Always fall back to user0@gmail.com
}

/**
 * Get default avatar based on email
 */
function getDefaultAvatar(email) {
    if (!email) {
        return 'https://ui-avatars.com/api/?name=User&background=00d4ff&color=fff&size=128';
    }
    const name = email.split('@')[0];
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=00d4ff&color=fff&size=128`;
}

/**
 * Fallback authentication - uses default user 0 (silently, no UI)
 */
function useFallbackAuth() {
    console.log('Using fallback user 0');
    currentUser = {
        id: '0',
        emailAddresses: [{ emailAddress: 'user0@gmail.com' }]
    };
    useClerk = false;
    // Don't update UI for fallback
}

/**
 * Check if user is signed in
 */
function isUserSignedIn() {
    return currentUser !== null;
}

/**
 * Get Clerk session token for authenticated API requests
 */
async function getSessionToken() {
    if (clerk && clerk.session) {
        try {
            return await clerk.session.getToken();
        } catch (error) {
            console.error('Error getting session token:', error);
        }
    }
    return null;
}

// Export functions for use in app.js
window.clerkAuth = {
    initialize: initializeClerk,
    getCurrentUserId,
    getCurrentUserEmail,
    isUserSignedIn,
    getSessionToken,
    getUser: () => currentUser
};
