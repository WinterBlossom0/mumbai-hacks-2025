// Content script - injected into web pages
// This script can interact with the DOM of web pages

console.log('Truth Lens content script loaded');

// Listen for messages from popup or background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractContent') {
        const content = extractPageContent();
        sendResponse({ content });
    }

    if (request.action === 'highlightClaims') {
        highlightClaims(request.claims);
        sendResponse({ success: true });
    }

    return true; // Keep message channel open for async response
});

/**
 * Extract main content from the current page
 */
function extractPageContent() {
    // Try to find article element first
    const article = document.querySelector('article');
    if (article) {
        return cleanText(article.innerText);
    }

    // Try common content selectors
    const selectors = [
        'main',
        '[role="main"]',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.story-body',
        '.article-body',
        '.content',
        '#content',
        '.main-content'
    ];

    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
            const text = cleanText(element.innerText);
            if (text && text.length > 100) {
                return text;
            }
        }
    }

    // Fallback to body, but try to filter out navigation and other noise
    const body = document.body.cloneNode(true);

    // Remove common noise elements
    const noiseSelectors = [
        'nav',
        'header',
        'footer',
        'aside',
        '.navigation',
        '.menu',
        '.sidebar',
        '.advertisement',
        '.ad',
        '.comments',
        'script',
        'style'
    ];

    noiseSelectors.forEach(selector => {
        const elements = body.querySelectorAll(selector);
        elements.forEach(el => el.remove());
    });

    return cleanText(body.innerText);
}

/**
 * Clean extracted text
 */
function cleanText(text) {
    if (!text) return '';

    return text
        .replace(/\s+/g, ' ') // Replace multiple spaces with single space
        .replace(/\n+/g, '\n') // Replace multiple newlines with single newline
        .trim();
}

/**
 * Highlight claims on the page (optional feature)
 */
function highlightClaims(claims) {
    if (!claims || claims.length === 0) return;

    // This is a basic implementation
    // You could make this more sophisticated
    claims.forEach(claim => {
        const text = claim.substring(0, 50); // Use first 50 chars to find
        highlightText(text);
    });
}

/**
 * Highlight specific text on the page
 */
function highlightText(searchText) {
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );

    const nodesToHighlight = [];
    let node;

    while (node = walker.nextNode()) {
        if (node.textContent.includes(searchText)) {
            nodesToHighlight.push(node);
        }
    }

    nodesToHighlight.forEach(node => {
        const span = document.createElement('span');
        span.style.backgroundColor = 'rgba(102, 126, 234, 0.3)';
        span.style.padding = '2px 4px';
        span.style.borderRadius = '3px';
        span.textContent = node.textContent;
        node.parentNode.replaceChild(span, node);
    });
}

/**
 * Get page metadata
 */
function getPageMetadata() {
    return {
        title: document.title,
        url: window.location.href,
        domain: window.location.hostname,
        description: document.querySelector('meta[name="description"]')?.content || '',
        author: document.querySelector('meta[name="author"]')?.content || '',
        publishDate: document.querySelector('meta[property="article:published_time"]')?.content || ''
    };
}
