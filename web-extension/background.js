// Background service worker for Edge/Chrome extension

// Import utility functions
importScripts('utils.js');

console.log('Truth Lens background service worker started');

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Truth Lens extension installed');

        // Set default settings
        chrome.storage.local.set({
            apiEndpoint: 'http://localhost:8000',
            autoCheck: false,
            showNotifications: true
        });

        // Open options page on first install
        chrome.runtime.openOptionsPage();
    } else if (details.reason === 'update') {
        console.log('Truth Lens extension updated');
    }
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'verifyContent') {
        handleVerifyContent(request.content, request.inputType)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Keep channel open for async response
    }

    if (request.action === 'updateBadge') {
        updateBadge(request.verdict, sender.tab?.id);
        sendResponse({ success: true });
    }

    return true;
});

/**
 * Handle content verification
 */
async function handleVerifyContent(content, inputType) {
    try {
        const settings = await chrome.storage.local.get(['apiEndpoint', 'userId', 'userEmail']);
        const apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';

        // Generate user ID if not exists
        let userId = settings.userId;
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            await chrome.storage.local.set({ userId });
        }

        let userEmail = settings.userEmail;
        if (!userEmail) {
            userEmail = `${userId}@truthlens.extension`;
            await chrome.storage.local.set({ userEmail });
        }

        const requestBody = {
            input_type: inputType,
            content: content,
            user_id: userId,
            user_email: userEmail
        };

        const response = await fetch(`${apiEndpoint}/api/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Cache the result
        await cacheVerification(data);

        // Show notification if enabled
        const showNotifications = (await chrome.storage.local.get(['showNotifications'])).showNotifications;
        if (showNotifications) {
            showVerificationNotification(data.verdict);
        }

        return {
            success: true,
            data: data
        };
    } catch (error) {
        console.error('Verification error:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Update extension badge
 */
function updateBadge(verdict, tabId) {
    if (!tabId) return;

    const badgeText = verdict ? '✓' : '✗';
    const badgeColor = verdict ? '#10b981' : '#ef4444';

    chrome.action.setBadgeText({ text: badgeText, tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: badgeColor, tabId: tabId });
}

/**
 * Show verification notification
 */
function showVerificationNotification(verdict) {
    const title = verdict ? 'Content Verified ✓' : 'Misinformation Detected ✗';
    const message = verdict
        ? 'The content appears to be accurate based on credible sources.'
        : 'The content may contain misinformation. Check the details in the extension.';

    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: title,
        message: message,
        priority: 2
    });
}

/**
 * Cache verification result
 */
async function cacheVerification(data) {
    const cache = await chrome.storage.local.get(['verificationCache']) || {};
    const verificationCache = cache.verificationCache || [];

    // Add new verification to cache
    verificationCache.unshift({
        ...data,
        timestamp: Date.now()
    });

    // Keep only last 50 verifications
    if (verificationCache.length > 50) {
        verificationCache.splice(50);
    }

    await chrome.storage.local.set({ verificationCache });
}

/**
 * Clear old cache entries (older than 7 days)
 */
async function clearOldCache() {
    const cache = await chrome.storage.local.get(['verificationCache']);
    const verificationCache = cache.verificationCache || [];

    const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    const filteredCache = verificationCache.filter(item => item.timestamp > sevenDaysAgo);

    await chrome.storage.local.set({ verificationCache: filteredCache });
}

// Clear old cache on startup
clearOldCache();

// Set up periodic cache cleanup (once per day)
chrome.alarms.create('clearCache', { periodInMinutes: 1440 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'clearCache') {
        clearOldCache();
    }
});
