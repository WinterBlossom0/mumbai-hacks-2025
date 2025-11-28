// Popup script - handles UI interactions and state management

let currentState = 'initial'; // initial, loading, results, error

// DOM Elements
const initialState = document.getElementById('initialState');
const loadingState = document.getElementById('loadingState');
const resultsState = document.getElementById('resultsState');
const errorState = document.getElementById('errorState');

const checkBtn = document.getElementById('checkBtn');
const checkAgainBtn = document.getElementById('checkAgainBtn');
const retryBtn = document.getElementById('retryBtn');
const settingsBtn = document.getElementById('settingsBtn');

const loadingMessage = document.getElementById('loadingMessage');
const verdictBadge = document.getElementById('verdictBadge');
const reasoning = document.getElementById('reasoning');
const claimsList = document.getElementById('claimsList');
const sourcesList = document.getElementById('sourcesList');
const errorMessage = document.getElementById('errorMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkBtn.addEventListener('click', handleCheck);
    checkAgainBtn.addEventListener('click', resetToInitial);
    retryBtn.addEventListener('click', handleCheck);
    settingsBtn.addEventListener('click', openSettings);
});

/**
 * Handle the check button click
 */
async function handleCheck() {
    try {
        // Get the current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab) {
            showError('Could not access the current tab');
            return;
        }

        // Show loading state
        showLoading();

        // Extract content from the page
        updateLoadingStep(0, 'Extracting content from page...');

        const content = await extractPageContent(tab);

        if (!content || content.trim().length < 50) {
            showError('Could not extract enough content from this page. Please try a different page with more text content.');
            return;
        }

        // Verify content with API
        updateLoadingStep(1, 'Discovering credible sources...');

        const result = await verifyContent(content, 'text');

        if (!result.success) {
            showError(result.error || 'Failed to verify content. Please check if the backend is running.');
            return;
        }

        updateLoadingStep(2, 'Analyzing claims...');

        // Small delay for better UX
        await new Promise(resolve => setTimeout(resolve, 500));

        // Show results
        showResults(result.data);

    } catch (error) {
        console.error('Error during verification:', error);
        showError(error.message || 'An unexpected error occurred');
    }
}

/**
 * Extract content from the current page
 */
async function extractPageContent(tab) {
    try {
        // Inject content script if needed
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            function: () => {
                // Extract main content from the page
                const article = document.querySelector('article');
                if (article) {
                    return article.innerText;
                }

                // Try common content selectors
                const selectors = [
                    'main',
                    '[role="main"]',
                    '.article-content',
                    '.post-content',
                    '.entry-content',
                    '.content',
                    'body'
                ];

                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        // Get text but filter out navigation, ads, etc.
                        const text = element.innerText;
                        if (text && text.length > 100) {
                            return text;
                        }
                    }
                }

                return document.body.innerText;
            }
        });

        return results[0]?.result || '';
    } catch (error) {
        console.error('Error extracting content:', error);
        throw new Error('Failed to extract content from page');
    }
}

/**
 * Show loading state
 */
function showLoading() {
    currentState = 'loading';
    hideAllStates();
    loadingState.classList.remove('hidden');
    updateLoadingStep(0, 'Extracting claims from the page');
}

/**
 * Update loading step
 */
function updateLoadingStep(stepIndex, message) {
    loadingMessage.textContent = message;

    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        if (index <= stepIndex) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

/**
 * Show results state
 */
function showResults(data) {
    currentState = 'results';
    hideAllStates();
    resultsState.classList.remove('hidden');

    // Set verdict badge
    verdictBadge.textContent = data.verdict ? '✓ Verified' : '✗ Misinformation Detected';
    verdictBadge.className = `verdict-badge ${data.verdict ? 'true' : 'false'}`;

    // Set reasoning
    reasoning.textContent = data.reasoning;

    // Set claims
    claimsList.innerHTML = '';
    if (data.claims && data.claims.length > 0) {
        data.claims.forEach(claim => {
            const li = document.createElement('li');
            li.textContent = claim;
            claimsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No specific claims extracted';
        claimsList.appendChild(li);
    }

    // Set sources
    sourcesList.innerHTML = '';
    if (data.sources && Object.keys(data.sources).length > 0) {
        // Flatten sources
        const allSources = new Set();
        Object.values(data.sources).forEach(urls => {
            urls.forEach(url => allSources.add(url));
        });

        Array.from(allSources).slice(0, 5).forEach(url => {
            const sourceItem = document.createElement('a');
            sourceItem.className = 'source-item';
            sourceItem.href = url;
            sourceItem.target = '_blank';
            sourceItem.innerHTML = `
                <svg class="source-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z" fill="currentColor"/>
                </svg>
                <span class="source-text">${extractDomain(url)}</span>
            `;
            sourcesList.appendChild(sourceItem);
        });
    } else {
        const noSources = document.createElement('div');
        noSources.className = 'source-item';
        noSources.textContent = 'No sources available';
        sourcesList.appendChild(noSources);
    }
}

/**
 * Show error state
 */
function showError(message) {
    currentState = 'error';
    hideAllStates();
    errorState.classList.remove('hidden');
    errorMessage.textContent = message;
}

/**
 * Reset to initial state
 */
function resetToInitial() {
    currentState = 'initial';
    hideAllStates();
    initialState.classList.remove('hidden');
}

/**
 * Hide all state views
 */
function hideAllStates() {
    initialState.classList.add('hidden');
    loadingState.classList.add('hidden');
    resultsState.classList.add('hidden');
    errorState.classList.add('hidden');
}

/**
 * Open settings page
 */
function openSettings() {
    chrome.runtime.openOptionsPage();
}
