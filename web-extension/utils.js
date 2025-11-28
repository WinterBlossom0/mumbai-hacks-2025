// Utility functions for the extension

/**
 * Get or create a unique user ID for this browser
 */
async function getUserId() {
    const result = await chrome.storage.local.get(['userId']);
    if (result.userId) {
        return result.userId;
    }

    // Generate a new user ID
    const userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    await chrome.storage.local.set({ userId });
    return userId;
}

/**
 * Get or create a user email (simplified for extension)
 */
async function getUserEmail() {
    const result = await chrome.storage.local.get(['userEmail']);
    if (result.userEmail) {
        return result.userEmail;
    }

    const userId = await getUserId();
    const userEmail = `${userId}@truthlens.extension`;
    await chrome.storage.local.set({ userEmail });
    return userEmail;
}

/**
 * Format a date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
}

/**
 * Truncate text to a maximum length
 */
function truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

/**
 * Extract domain from URL
 */
function extractDomain(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname.replace('www.', '');
    } catch (e) {
        return url;
    }
}

/**
 * Show a notification (only works in background context)
 */
function showNotification(title, message, type = 'info') {
    if (typeof chrome !== 'undefined' && chrome.notifications) {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: title,
            message: message,
            priority: 2
        });
    }
}

/**
 * Get API endpoint from settings
 */
async function getApiEndpoint() {
    const result = await chrome.storage.local.get(['apiEndpoint']);
    return result.apiEndpoint || 'https://truthlens-web-extension-backend.onrender.com';
}

/**
 * Set API endpoint in settings
 */
async function setApiEndpoint(endpoint) {
    await chrome.storage.local.set({ apiEndpoint: endpoint });
}
