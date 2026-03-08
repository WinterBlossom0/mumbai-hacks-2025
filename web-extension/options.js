// Options page script

document.addEventListener('DOMContentLoaded', loadSettings);

const apiEndpointInput = document.getElementById('apiEndpoint');
const showNotificationsCheckbox = document.getElementById('showNotifications');
const userIdInput = document.getElementById('userId');
const userEmailInput = document.getElementById('userEmail');
const saveBtn = document.getElementById('saveBtn');
const testBtn = document.getElementById('testBtn');
const statusMessage = document.getElementById('statusMessage');

// Check if running in extension context
function isExtensionContext() {
    return typeof chrome !== 'undefined' && chrome.runtime && chrome.storage;
}

// Load settings from storage
async function loadSettings() {
    if (!isExtensionContext()) {
        showStatus('Error: Not running in extension context. Please install the extension.', 'error');
        return;
    }

    try {
        const settings = await chrome.storage.local.get([
            'apiEndpoint',
            'showNotifications',
            'userId',
            'userEmail'
        ]);

        apiEndpointInput.value = settings.apiEndpoint || 'https://truthlens-web-extension-backend.onrender.com';
        showNotificationsCheckbox.checked = settings.showNotifications !== false; // Default to true

        // Generate user ID if not exists
        let userId = settings.userId;
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            await chrome.storage.local.set({ userId });
        }
        userIdInput.value = userId;

        let userEmail = settings.userEmail;
        if (!userEmail) {
            userEmail = `${userId}@truthlens.extension`;
            await chrome.storage.local.set({ userEmail });
        }
        userEmailInput.value = userEmail;
    } catch (error) {
        console.error('Error loading settings:', error);
        showStatus(`Error loading settings: ${error.message}`, 'error');
    }
}

// Save settings
saveBtn.addEventListener('click', async () => {
    if (!isExtensionContext()) {
        showStatus('Error: Cannot save settings outside extension context.', 'error');
        return;
    }

    const apiEndpoint = apiEndpointInput.value.trim();

    // Validate API endpoint
    if (!apiEndpoint) {
        showStatus('Please enter a valid API endpoint', 'error');
        return;
    }

    // Remove trailing slash if present
    const cleanEndpoint = apiEndpoint.replace(/\/$/, '');

    try {
        await chrome.storage.local.set({
            apiEndpoint: cleanEndpoint,
            showNotifications: showNotificationsCheckbox.checked
        });

        showStatus('Settings saved successfully!', 'success');
    } catch (error) {
        console.error('Error saving settings:', error);
        showStatus(`Error saving settings: ${error.message}`, 'error');
    }
});

// Test API connection
testBtn.addEventListener('click', async () => {
    const apiEndpoint = apiEndpointInput.value.trim().replace(/\/$/, '');

    if (!apiEndpoint) {
        showStatus('Please enter a valid API endpoint', 'error');
        return;
    }

    showStatus('Testing connection...', 'success');

    try {
        const response = await fetch(`${apiEndpoint}/test`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'ok') {
            showStatus('✓ Connection successful! Backend is running.', 'success');
        } else {
            showStatus('Connection established but received unexpected response', 'error');
        }
    } catch (error) {
        console.error('Connection test failed:', error);
        showStatus(`✗ Connection failed: ${error.message}. Make sure the backend is running.`, 'error');
    }
});

// Show status message
function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';

    // Hide after 5 seconds
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}
