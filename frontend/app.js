const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://eyeoftruth.onrender.com';

// Initialize Clerk authentication when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...');
    
    // Initialize Clerk auth
    if (window.clerkAuth) {
        window.clerkAuth.initialize();
    }

    // Setup category filter listeners first
    setupCategoryFilters();

    // Load public feed
    loadPublicFeed();

    // Load news ticker
    loadNewsTicker();
});

// Setup category filter listeners
function setupCategoryFilters() {
    const filterButtons = document.querySelectorAll('.category-filter-bar .filter-btn');
    const heroSection = document.querySelector('.hero');
    
    console.log('Found filter buttons:', filterButtons.length);
    console.log('Found hero section:', heroSection);
    
    if (filterButtons.length === 0) {
        console.error('No filter buttons found!');
        return;
    }
    
    filterButtons.forEach((btn, index) => {
        const category = btn.getAttribute('data-category');
        console.log(`Setting up button ${index}: ${category}`);
        
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('Button clicked:', category);
            
            // Remove active class from all buttons
            filterButtons.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Hide/show hero section based on filter
            if (heroSection) {
                if (category === 'all') {
                    heroSection.style.display = 'block';
                } else {
                    heroSection.style.display = 'none';
                }
            }
            
            // Load filtered feed
            loadPublicFeed(category);
        });
    });
    
    console.log('Category filters setup complete');
}

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = e.target.dataset.page;

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        e.target.classList.add('active');

        // Show corresponding page
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(`${page}-page`).classList.add('active');

        // Load data based on page
        if (page === 'history') {
            loadHistory();
        } else if (page === 'home') {
            loadPublicFeed();
        } else if (page === 'reddit') {
            loadRedditFeed();
        }
    });
});

async function loadRedditFeed() {
    const feedContainer = document.getElementById('reddit-feed');
    feedContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading Reddit feed...</p></div>';

    try {
        const response = await fetch(`${API_URL}/api/reddit-posts?limit=50`);
        if (!response.ok) {
            throw new Error('Failed to fetch Reddit feed');
        }

        const feed = await response.json();

        if (feed.length === 0) {
            feedContainer.innerHTML = '<div class="empty-history">No verified Reddit posts yet</div>';
            return;
        }

        feedContainer.innerHTML = '';
        feed.forEach((item) => {
            const feedItem = document.createElement('div');
            feedItem.className = 'feed-item';
            feedItem.id = `reddit-post-${item.id}`;
            feedItem.style.cursor = 'pointer';
            feedItem.style.transition = 'all 0.3s ease';

            const header = document.createElement('div');
            header.className = 'feed-item-header';

            const userInfo = document.createElement('span');
            userInfo.className = 'feed-user-info';
            userInfo.textContent = `u/${item.author}`;

            const date = document.createElement('span');
            date.className = 'history-date';
            date.textContent = new Date(item.created_at).toLocaleDateString();

            header.appendChild(userInfo);
            header.appendChild(date);

            feedItem.appendChild(header);

            // Headline (if available)
            if (item.headline) {
                const headline = document.createElement('h3');
                headline.className = 'feed-headline';
                headline.textContent = item.headline;
                headline.style.marginTop = '0.5rem';
                headline.style.marginBottom = '0.5rem';
                headline.style.fontSize = '1.2rem';
                headline.style.fontWeight = '600';
                headline.style.color = 'var(--text-primary)';
                feedItem.appendChild(headline);
            }

            // Content container (title + body)
            const content = document.createElement('div');
            content.className = 'feed-content';
            content.textContent = item.body || item.url || item.title;

            if (item.headline) {
                content.style.display = 'none'; // Hide content initially if headline exists
                content.style.marginTop = '0.5rem';
                content.style.padding = '0.5rem';
                content.style.background = 'rgba(0,0,0,0.2)';
                content.style.borderRadius = '4px';
            } else {
                // Truncate Style
                content.style.display = '-webkit-box';
                content.style.webkitLineClamp = '3';
                content.style.webkitBoxOrient = 'vertical';
                content.style.overflow = 'hidden';
                content.style.marginBottom = '0.5rem';
            }

            feedItem.appendChild(content);

            // "Read More" indicator
            const readMore = document.createElement('div');
            readMore.className = 'read-more-indicator';
            readMore.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.8rem;">▼ Expand details</span>';
            readMore.style.textAlign = 'center';
            readMore.style.marginTop = '0.5rem';
            feedItem.appendChild(readMore);

            // Expandable details section
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'feed-details hidden';
            detailsDiv.style.marginTop = '1rem';
            detailsDiv.style.paddingTop = '1rem';
            detailsDiv.style.borderTop = '1px solid rgba(255, 255, 255, 0.1)';

            detailsDiv.innerHTML = `
                <div class="feed-reasoning" style="margin-bottom: 1rem;">
                    <h4 style="color: var(--accent-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🤖</span> AI Analysis
                    </h4>
                    <p style="line-height: 1.6; color: var(--text-secondary);">${item.reasoning}</p>
                </div>
                <div class="feed-claims">
                    <h4 style="color: var(--accent-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>📌</span> Key Claims
                    </h4>
                    <ul style="padding-left: 1.5rem; color: var(--text-secondary); space-y: 0.5rem;">
                        ${item.claims.map(claim => `<li style="margin-bottom: 0.5rem;">${claim}</li>`).join('')}
                    </ul>
                </div>
            `;
            feedItem.appendChild(detailsDiv);

            // Toggle expansion on click
            feedItem.addEventListener('click', () => {
                const isHidden = detailsDiv.classList.contains('hidden');

                if (isHidden) {
                    // Expand
                    detailsDiv.classList.remove('hidden');

                    if (item.headline) {
                        content.style.display = 'block'; // Show content
                    } else {
                        // COMPLETELY REMOVE TRUNCATION
                        content.style.display = 'block';
                        content.style.webkitLineClamp = 'unset';
                        content.style.overflow = 'visible';
                        content.style.maxHeight = 'none';
                    }

                    readMore.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.8rem;">▲ Collapse</span>';
                } else {
                    // Collapse
                    detailsDiv.classList.add('hidden');

                    if (item.headline) {
                        content.style.display = 'none'; // Hide content again
                    } else {
                        // RE-TRUNCATE
                        content.style.display = '-webkit-box';
                        content.style.webkitLineClamp = '3';
                        content.style.webkitBoxOrient = 'vertical';
                        content.style.overflow = 'hidden';
                    }

                    readMore.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.8rem;">▼ Expand details</span>';
                }
            });

            feedContainer.appendChild(feedItem);
        });
    } catch (error) {
        console.error('Error loading Reddit feed:', error);
        feedContainer.innerHTML = '<div class="error-message">Failed to load Reddit feed</div>';
    }
}

async function loadPublicFeed(category = 'all') {
    const feedContainer = document.getElementById('public-feed');
    feedContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading public feed...</p></div>';

    try {
        const response = await fetch(`${API_URL}/api/public-feed?limit=50`);
        if (!response.ok) {
            throw new Error('Failed to fetch public feed');
        }

        let feed = await response.json();
        
        console.log('Fetched feed:', feed);
        console.log('Filtering by category:', category);

        // Filter by category if not 'all'
        if (category !== 'all') {
            feed = feed.filter(item => {
                console.log('Item category:', item.category, 'Expected:', category);
                return item.category === category;
            });
        }
        
        console.log('Filtered feed length:', feed.length);

        if (feed.length === 0) {
            feedContainer.innerHTML = `<div class="empty-history">No ${category === 'all' ? '' : category + ' '}verifications found</div>`;
            return;
        }

        feedContainer.innerHTML = '';
        feed.forEach((item) => {
            const feedItem = document.createElement('div');
            feedItem.className = 'feed-item';
            feedItem.id = `post-${item.id}`;
            feedItem.style.cursor = 'pointer';
            feedItem.style.transition = 'all 0.3s ease';

            const header = document.createElement('div');
            header.className = 'feed-item-header';

            const currentUserEmailForVerdict = window.clerkAuth ? window.clerkAuth.getCurrentUserEmail() : null;
            const isOwnPostForVerdict = currentUserEmailForVerdict && item.user_email.toLowerCase() === currentUserEmailForVerdict.toLowerCase();
            const revealClass = isOwnPostForVerdict ? '' : 'reveal-on-hover';

            const verdict = document.createElement('span');
            verdict.className = `history-verdict ${item.verdict ? 'true' : 'false'} ${revealClass}`;
            verdict.textContent = item.verdict ? 'TRUE' : 'FALSE';

            const userInfo = document.createElement('span');
            userInfo.className = 'feed-user-info';
            userInfo.textContent = `by ${item.user_email.split('@')[0]}`;

            const date = document.createElement('span');
            date.className = 'history-date';
            date.textContent = new Date(item.created_at).toLocaleDateString();

            header.appendChild(verdict);
            header.appendChild(userInfo);
            header.appendChild(date);

            feedItem.appendChild(header);

            // Headline (if available)
            if (item.headline) {
                const headline = document.createElement('h3');
                headline.className = 'feed-headline';
                headline.textContent = item.headline;
                headline.style.marginTop = '0.5rem';
                headline.style.marginBottom = '0.5rem';
                headline.style.fontSize = '1.2rem';
                headline.style.fontWeight = '600';
                headline.style.color = 'var(--text-primary)';
                feedItem.appendChild(headline);
            }

            // Content container
            const content = document.createElement('div');
            content.className = 'feed-content';
            content.textContent = item.input_content;

            if (item.headline) {
                content.style.display = 'none'; // Hide content initially if headline exists
                content.style.marginTop = '0.5rem';
                content.style.padding = '0.5rem';
                content.style.background = 'rgba(0,0,0,0.2)';
                content.style.borderRadius = '4px';
            } else {
                // Initial Truncate Style
                content.style.display = '-webkit-box';
                content.style.webkitLineClamp = '3';
                content.style.webkitBoxOrient = 'vertical';
                content.style.overflow = 'hidden';
                content.style.marginBottom = '0.5rem';
            }

            feedItem.appendChild(content);

            // "Read More" indicator
            const readMore = document.createElement('div');
            readMore.className = 'read-more-indicator';
            readMore.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.8rem;">▼ Expand details</span>';
            readMore.style.textAlign = 'center';
            readMore.style.marginTop = '0.5rem';
            feedItem.appendChild(readMore);

            // Vote Actions - only show if not own post
            const currentUserEmailForVote = window.clerkAuth ? window.clerkAuth.getCurrentUserEmail() : null;
            const isOwnPostForVote = currentUserEmailForVote && item.user_email.toLowerCase() === currentUserEmailForVote.toLowerCase();

            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'feed-actions';
            actionsDiv.style.display = 'flex';
            actionsDiv.style.gap = '1rem';
            actionsDiv.style.marginTop = '0.5rem';
            actionsDiv.style.borderTop = '1px solid rgba(255,255,255,0.1)';
            actionsDiv.style.paddingTop = '0.5rem';

            if (!isOwnPostForVote) {
                // Upvote
                const upvoteBtn = document.createElement('button');
                upvoteBtn.className = 'vote-btn upvote';
                upvoteBtn.style.background = 'none';
                upvoteBtn.style.border = 'none';
                upvoteBtn.style.color = 'var(--text-secondary)';
                upvoteBtn.style.cursor = 'pointer';
                upvoteBtn.style.display = 'flex';
                upvoteBtn.style.alignItems = 'center';
                upvoteBtn.style.gap = '0.3rem';
                upvoteBtn.innerHTML = `⬆️ <span class="count">${item.upvotes || 0}</span>`;
                upvoteBtn.onclick = (e) => {
                    e.stopPropagation(); // Prevent card expansion
                    handleVote(item.id, 1, upvoteBtn, downvoteBtn);
                };

                // Downvote
                const downvoteBtn = document.createElement('button');
                downvoteBtn.className = 'vote-btn downvote';
                downvoteBtn.style.background = 'none';
                downvoteBtn.style.border = 'none';
                downvoteBtn.style.color = 'var(--text-secondary)';
                downvoteBtn.style.cursor = 'pointer';
                downvoteBtn.style.display = 'flex';
                downvoteBtn.style.alignItems = 'center';
                downvoteBtn.style.gap = '0.3rem';
                downvoteBtn.innerHTML = `⬇️ <span class="count">${item.downvotes || 0}</span>`;
                downvoteBtn.onclick = (e) => {
                    e.stopPropagation();
                    handleVote(item.id, -1, upvoteBtn, downvoteBtn);
                };

                actionsDiv.appendChild(upvoteBtn);
                actionsDiv.appendChild(downvoteBtn);
            } else {
                // Show vote counts only for own posts
                const voteCount = document.createElement('div');
                voteCount.style.color = 'var(--text-secondary)';
                voteCount.style.fontSize = '0.85rem';
                voteCount.style.fontStyle = 'italic';
                voteCount.innerHTML = `${item.upvotes || 0} upvotes • ${item.downvotes || 0} downvotes`;
                actionsDiv.appendChild(voteCount);
            }

            feedItem.appendChild(actionsDiv);

            // Expandable details section
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'feed-details hidden';
            detailsDiv.style.marginTop = '1rem';
            detailsDiv.style.paddingTop = '1rem';
            detailsDiv.style.borderTop = '1px solid rgba(255, 255, 255, 0.1)';

            detailsDiv.innerHTML = `
                <div class="feed-reasoning" style="margin-bottom: 1rem;">
                    <h4 style="color: var(--accent-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>🤖</span> AI Analysis
                    </h4>
                    <p style="line-height: 1.6; color: var(--text-secondary);">${item.reasoning}</p>
                </div>
                <div class="feed-claims">
                    <h4 style="color: var(--accent-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span>📌</span> Key Claims
                    </h4>
                    <ul style="padding-left: 1.5rem; color: var(--text-secondary); space-y: 0.5rem;">
                        ${item.claims.map(claim => `<li style="margin-bottom: 0.5rem;">${claim}</li>`).join('')}
                    </ul>
                </div>
            `;
            feedItem.appendChild(detailsDiv);

            // Toggle expansion on click
            feedItem.addEventListener('click', () => {
                const isHidden = detailsDiv.classList.contains('hidden');

                if (isHidden) {
                    // Expand
                    detailsDiv.classList.remove('hidden');

                    if (item.headline) {
                        content.style.display = 'block'; // Show content
                    } else {
                        // COMPLETELY REMOVE TRUNCATION
                        content.style.display = 'block';
                        content.style.webkitLineClamp = 'unset';
                        content.style.overflow = 'visible';
                        content.style.maxHeight = 'none';
                    }

                    readMore.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.8rem;">▲ Show less</span>';
                    feedItem.style.background = 'rgba(255, 255, 255, 0.08)';
                } else {
                    // Collapse
                    detailsDiv.classList.add('hidden');

                    if (item.headline) {
                        content.style.display = 'none'; // Hide content
                    } else {
                        // RE-APPLY TRUNCATION
                        content.style.display = '-webkit-box';
                        content.style.webkitLineClamp = '3';
                        content.style.webkitBoxOrient = 'vertical';
                        content.style.overflow = 'hidden';
                    }

                    readMore.innerHTML = '<span style="color: var(--text-secondary); font-size: 0.8rem;">▼ Expand details</span>';
                    feedItem.style.background = '';
                }
            });

            feedContainer.appendChild(feedItem);
        });
    } catch (error) {
        console.error('Error loading public feed:', error);
        feedContainer.innerHTML = '<div class="empty-history">Failed to load public feed</div>';
    }
}

// Input type selector
document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');

        const type = e.target.dataset.type;
        const textInput = document.getElementById('text-input');
        const urlInput = document.getElementById('url-input');

        if (type === 'text') {
            textInput.classList.remove('hidden');
            urlInput.classList.add('hidden');
        } else {
            textInput.classList.add('hidden');
            urlInput.classList.remove('hidden');
        }
    });
});

// Verify button
document.getElementById('verify-btn').addEventListener('click', async () => {
    const activeType = document.querySelector('.type-btn.active').dataset.type;
    const content = activeType === 'text'
        ? document.getElementById('text-input').value
        : document.getElementById('url-input').value;

    if (!content.trim()) {
        alert('Please enter content to verify');
        return;
    }

    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('verify-btn').disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input_type: activeType,
                content: content,
                user_id: window.clerkAuth ? window.clerkAuth.getCurrentUserId() : '0',
                user_email: window.clerkAuth ? window.clerkAuth.getCurrentUserEmail() : 'user0@gmail.com'
            })
        });

        if (!response.ok) {
            // Get error details from backend
            let errorMessage = 'Verification failed';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();

        console.log('Verification response:', data);

        // Display result
        displayResult(data);

        // Reload history from server
        await loadHistoryFromServer();

    } catch (error) {
        console.error('Verification error:', error);
        alert('Error: ' + error.message + '\n\nPlease check:\n1. All API keys are set in .env\n2. Backend console for more details');
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('verify-btn').disabled = false;
    }
});

function displayResult(data) {
    const resultDiv = document.getElementById('result');
    const verdictBadge = document.getElementById('verdict-badge');
    const verdictText = document.getElementById('verdict-text');
    const reasoningText = document.getElementById('reasoning-text');
    const claimsList = document.getElementById('claims-list');
    const sourcesList = document.getElementById('sources-list');

    // Verdict
    verdictBadge.className = `verdict-badge ${data.verdict ? 'true' : 'false'}`;
    verdictText.textContent = data.verdict ? 'TRUE' : 'FALSE';

    // Reasoning
    reasoningText.textContent = data.reasoning;

    // Claims
    claimsList.innerHTML = '';
    data.claims.forEach(claim => {
        const li = document.createElement('li');
        li.textContent = claim;
        claimsList.appendChild(li);
    });

    // Sources
    sourcesList.innerHTML = '';
    Object.entries(data.website_claims).forEach(([url, claims]) => {
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'source-item';

        const urlLink = document.createElement('a');
        urlLink.href = url;
        urlLink.target = '_blank';
        urlLink.textContent = url;

        const claimsCount = document.createElement('h4');
        claimsCount.textContent = `${claims.length} claims found`;

        sourceDiv.appendChild(claimsCount);
        sourceDiv.appendChild(urlLink);
        sourcesList.appendChild(sourceDiv);
    });

    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// History functions
async function loadHistoryFromServer() {
    const userId = window.clerkAuth ? window.clerkAuth.getCurrentUserId() : '0';

    try {
        const response = await fetch(`${API_URL}/api/history/${userId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch history');
        }
        const history = await response.json();

        // Also save to localStorage as backup
        localStorage.setItem('verificationHistory', JSON.stringify(history));

        return history;
    } catch (error) {
        console.error('Error loading history from server:', error);
        // Fallback to localStorage
        return JSON.parse(localStorage.getItem('verificationHistory') || '[]');
    }
}

async function loadHistory() {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading history...</p></div>';

    const history = await loadHistoryFromServer();

    if (history.length === 0) {
        historyList.innerHTML = '<div class="empty-history">No verification history yet</div>';
        return;
    }

    historyList.innerHTML = '';
    history.forEach((item) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        const header = document.createElement('div');
        header.className = 'history-item-header';

        const leftSection = document.createElement('div');
        leftSection.style.display = 'flex';
        leftSection.style.gap = '1rem';
        leftSection.style.alignItems = 'center';

        const verdict = document.createElement('span');
        verdict.className = `history-verdict ${item.verdict ? 'true' : 'false'}`;
        verdict.textContent = item.verdict ? 'TRUE' : 'FALSE';

        const date = document.createElement('span');
        date.className = 'history-date';
        date.textContent = new Date(item.created_at).toLocaleString();

        leftSection.appendChild(verdict);
        leftSection.appendChild(date);

        // Public toggle
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'toggle-container';
        toggleContainer.onclick = (e) => e.stopPropagation();

        const toggleLabel = document.createElement('label');
        toggleLabel.className = 'toggle-switch';

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.checked = item.is_public;
        toggleInput.onchange = async (e) => {
            e.stopPropagation();
            await togglePublicStatus(item.id, toggleInput.checked);
        };

        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'toggle-slider';

        const toggleText = document.createElement('span');
        toggleText.className = 'toggle-text';
        toggleText.textContent = 'Public';

        toggleLabel.appendChild(toggleInput);
        toggleLabel.appendChild(toggleSlider);
        toggleContainer.appendChild(toggleLabel);
        toggleContainer.appendChild(toggleText);

        header.appendChild(leftSection);
        header.appendChild(toggleContainer);

        const content = document.createElement('div');
        content.className = 'history-content';
        content.textContent = item.input_content;

        historyItem.appendChild(header);
        historyItem.appendChild(content);

        historyItem.addEventListener('click', () => {
            showHistoryDetail(item);
        });

        historyList.appendChild(historyItem);
    });
}

async function togglePublicStatus(verificationId, isPublic) {
    try {
        const response = await fetch(`${API_URL}/api/toggle-public/${verificationId}?is_public=${isPublic}`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Failed to toggle public status');
        }

        console.log('Public status updated');
    } catch (error) {
        console.error('Error toggling public status:', error);
        alert('Failed to update public status');
    }
}

function showHistoryDetail(item) {
    displayResult({
        verdict: item.verdict,
        reasoning: item.reasoning,
        claims: item.claims,
        website_claims: {}
    });

    // Switch to verify page to show result
    document.querySelector('[data-page="verify"]').click();
}

async function handleVote(verificationId, voteType, upBtn, downBtn) {
    if (!window.clerkAuth || !window.clerkAuth.getCurrentUserId()) {
        alert("Please sign in to vote!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                verification_id: verificationId,
                user_id: window.clerkAuth.getCurrentUserId(),
                vote_type: voteType
            })
        });

        if (response.ok) {
            const data = await response.json();
            upBtn.querySelector('.count').textContent = data.upvotes;
            downBtn.querySelector('.count').textContent = data.downvotes;
        } else {
            alert("Failed to vote");
        }
    } catch (e) {
        console.error("Vote error:", e);
    }
}



// History functions
async function loadHistoryFromServer() {
    const userId = window.clerkAuth ? window.clerkAuth.getCurrentUserId() : '0';

    try {
        const response = await fetch(`${API_URL}/api/history/${userId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch history');
        }
        const history = await response.json();

        // Also save to localStorage as backup
        localStorage.setItem('verificationHistory', JSON.stringify(history));

        return history;
    } catch (error) {
        console.error('Error loading history from server:', error);
        // Fallback to localStorage
        return JSON.parse(localStorage.getItem('verificationHistory') || '[]');
    }
}

async function loadHistory() {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading history...</p></div>';

    const history = await loadHistoryFromServer();

    if (history.length === 0) {
        historyList.innerHTML = '<div class="empty-history">No verification history yet</div>';
        return;
    }

    historyList.innerHTML = '';
    history.forEach((item) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        const header = document.createElement('div');
        header.className = 'history-item-header';

        const leftSection = document.createElement('div');
        leftSection.style.display = 'flex';
        leftSection.style.gap = '1rem';
        leftSection.style.alignItems = 'center';

        const verdict = document.createElement('span');
        verdict.className = `history-verdict ${item.verdict ? 'true' : 'false'}`;
        verdict.textContent = item.verdict ? 'TRUE' : 'FALSE';

        const date = document.createElement('span');
        date.className = 'history-date';
        date.textContent = new Date(item.created_at).toLocaleString();

        leftSection.appendChild(verdict);
        leftSection.appendChild(date);

        // Public toggle
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'toggle-container';
        toggleContainer.onclick = (e) => e.stopPropagation();

        const toggleLabel = document.createElement('label');
        toggleLabel.className = 'toggle-switch';

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.checked = item.is_public;
        toggleInput.onchange = async (e) => {
            e.stopPropagation();
            await togglePublicStatus(item.id, toggleInput.checked);
        };

        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'toggle-slider';

        const toggleText = document.createElement('span');
        toggleText.className = 'toggle-text';
        toggleText.textContent = 'Public';

        toggleLabel.appendChild(toggleInput);
        toggleLabel.appendChild(toggleSlider);
        toggleContainer.appendChild(toggleLabel);
        toggleContainer.appendChild(toggleText);

        header.appendChild(leftSection);
        header.appendChild(toggleContainer);

        const content = document.createElement('div');
        content.className = 'history-content';
        content.textContent = item.input_content;

        historyItem.appendChild(header);
        historyItem.appendChild(content);

        historyItem.addEventListener('click', () => {
            showHistoryDetail(item);
        });

        historyList.appendChild(historyItem);
    });
}

async function togglePublicStatus(verificationId, isPublic) {
    try {
        const response = await fetch(`${API_URL}/api/toggle-public/${verificationId}?is_public=${isPublic}`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Failed to toggle public status');
        }

        console.log('Public status updated');
    } catch (error) {
        console.error('Error toggling public status:', error);
        alert('Failed to update public status');
    }
}

function showHistoryDetail(item) {
    displayResult({
        verdict: item.verdict,
        reasoning: item.reasoning,
        claims: item.claims,
        website_claims: {}
    });

    // Switch to verify page to show result
    document.querySelector('[data-page="verify"]').click();
}

async function handleVote(verificationId, voteType, upBtn, downBtn) {
    if (!window.clerkAuth || !window.clerkAuth.getCurrentUserId()) {
        alert("Please sign in to vote!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                verification_id: verificationId,
                user_id: window.clerkAuth.getCurrentUserId(),
                vote_type: voteType
            })
        });

        if (response.ok) {
            const data = await response.json();
            upBtn.querySelector('.count').textContent = data.upvotes;
            downBtn.querySelector('.count').textContent = data.downvotes;
        } else {
            alert("Failed to vote");
        }
    } catch (e) {
        console.error("Vote error:", e);
    }
}

async function loadNewsTicker() {
    try {
        const response = await fetch(`${API_URL}/api/top-headlines?limit=9`);
        if (!response.ok) throw new Error('Failed to fetch headlines');
        const headlines = await response.json();

        if (headlines.length === 0) return;

        const bands = [
            document.getElementById('ticker-band-1'),
            document.getElementById('ticker-band-2'),
            document.getElementById('ticker-band-3')
        ];

        // Configure directions: L->R, R->L, L->R
        bands[0].className = 'ticker-band right';
        bands[1].className = 'ticker-band left';
        bands[2].className = 'ticker-band right';

        const createItem = (item) => {
            const div = document.createElement('div');
            div.className = 'ticker-item';
            div.innerHTML = `<span>🔥</span> ${item.headline || item.input_content.substring(0, 50) + '...'}`;
            div.onclick = () => {
                scrollToPost(item.id);
            };
            return div;
        };

        const populateBand = (band, items) => {
            if (!items.length || !band) return;
            band.innerHTML = '';
            // Repeat items to ensure smooth scrolling
            for (let i = 0; i < 6; i++) {
                items.forEach(item => {
                    band.appendChild(createItem(item));
                });
            }
        };

        // Distribute headlines
        let chunk1 = [], chunk2 = [], chunk3 = [];

        if (headlines.length >= 3) {
            chunk1 = headlines.slice(0, 3);
            chunk2 = headlines.slice(3, 6);
            chunk3 = headlines.slice(6, 9);
        } else {
            chunk1 = headlines;
            chunk2 = headlines;
            chunk3 = headlines;
        }

        // Fallback if chunks are empty but we have headlines
        if (chunk2.length === 0 && headlines.length > 0) chunk2 = headlines;
        if (chunk3.length === 0 && headlines.length > 0) chunk3 = headlines;

        populateBand(bands[0], chunk1);
        populateBand(bands[1], chunk2);
        populateBand(bands[2], chunk3);

    } catch (e) {
        console.error("Error loading ticker:", e);
        historyList.innerHTML = '<div class="empty-history">No verification history yet</div>';
        return;
    }

    historyList.innerHTML = '';
    history.forEach((item) => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        const header = document.createElement('div');
        header.className = 'history-item-header';

        const leftSection = document.createElement('div');
        leftSection.style.display = 'flex';
        leftSection.style.gap = '1rem';
        leftSection.style.alignItems = 'center';

        const verdict = document.createElement('span');
        verdict.className = `history-verdict ${item.verdict ? 'true' : 'false'}`;
        verdict.textContent = item.verdict ? 'TRUE' : 'FALSE';

        const date = document.createElement('span');
        date.className = 'history-date';
        date.textContent = new Date(item.created_at).toLocaleString();

        leftSection.appendChild(verdict);
        leftSection.appendChild(date);

        // Public toggle
        const toggleContainer = document.createElement('div');
        toggleContainer.className = 'toggle-container';
        toggleContainer.onclick = (e) => e.stopPropagation();

        const toggleLabel = document.createElement('label');
        toggleLabel.className = 'toggle-switch';

        const toggleInput = document.createElement('input');
        toggleInput.type = 'checkbox';
        toggleInput.checked = item.is_public;
        toggleInput.onchange = async (e) => {
            e.stopPropagation();
            await togglePublicStatus(item.id, toggleInput.checked);
        };

        const toggleSlider = document.createElement('span');
        toggleSlider.className = 'toggle-slider';

        const toggleText = document.createElement('span');
        toggleText.className = 'toggle-text';
        toggleText.textContent = 'Public';

        toggleLabel.appendChild(toggleInput);
        toggleLabel.appendChild(toggleSlider);
        toggleContainer.appendChild(toggleLabel);
        toggleContainer.appendChild(toggleText);

        header.appendChild(leftSection);
        header.appendChild(toggleContainer);

        const content = document.createElement('div');
        content.className = 'history-content';
        content.textContent = item.input_content;

        historyItem.appendChild(header);
        historyItem.appendChild(content);

        historyItem.addEventListener('click', () => {
            showHistoryDetail(item);
        });

        historyList.appendChild(historyItem);
    });
}

async function togglePublicStatus(verificationId, isPublic) {
    try {
        const response = await fetch(`${API_URL}/api/toggle-public/${verificationId}?is_public=${isPublic}`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error('Failed to toggle public status');
        }

        console.log('Public status updated');
    } catch (error) {
        console.error('Error toggling public status:', error);
        alert('Failed to update public status');
    }
}

function showHistoryDetail(item) {
    displayResult({
        verdict: item.verdict,
        reasoning: item.reasoning,
        claims: item.claims,
        website_claims: {}
    });

    // Switch to verify page to show result
    document.querySelector('[data-page="verify"]').click();
}

async function handleVote(verificationId, voteType, upBtn, downBtn) {
    if (!window.clerkAuth || !window.clerkAuth.getCurrentUserId()) {
        alert("Please sign in to vote!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                verification_id: verificationId,
                user_id: window.clerkAuth.getCurrentUserId(),
                vote_type: voteType
            })
        });

        if (response.ok) {
            const data = await response.json();
            upBtn.querySelector('.count').textContent = data.upvotes;
            downBtn.querySelector('.count').textContent = data.downvotes;
        } else {
            alert("Failed to vote");
        }
    } catch (e) {
        console.error("Vote error:", e);
    }
}

async function loadNewsTicker() {
    try {
        const response = await fetch(`${API_URL}/api/top-headlines?limit=9`);
        if (!response.ok) throw new Error('Failed to fetch headlines');
        const headlines = await response.json();

        if (headlines.length === 0) return;

        const bands = [
            document.getElementById('ticker-band-1'),
            document.getElementById('ticker-band-2'),
            document.getElementById('ticker-band-3')
        ];

        // Configure directions: L->R, R->L, L->R
        bands[0].className = 'ticker-band right';
        bands[1].className = 'ticker-band left';
        bands[2].className = 'ticker-band right';

        const createItem = (item) => {
            const div = document.createElement('div');
            div.className = 'ticker-item';
            div.innerHTML = `• ${item.headline || item.input_content.substring(0, 50) + '...'}`;
            div.onclick = () => {
                displayPostInHero(item);
            };
            return div;
        };

        const populateBand = (band, items) => {
            if (!items.length || !band) return;
            band.innerHTML = '';
            // Repeat items to ensure smooth scrolling
            for (let i = 0; i < 6; i++) {
                items.forEach(item => {
                    band.appendChild(createItem(item));
                });
            }
        };

        // Distribute headlines
        let chunk1 = [], chunk2 = [], chunk3 = [];

        if (headlines.length >= 3) {
            chunk1 = headlines.slice(0, 3);
            chunk2 = headlines.slice(3, 6);
            chunk3 = headlines.slice(6, 9);
        } else {
            chunk1 = headlines;
            chunk2 = headlines;
            chunk3 = headlines;
        }

        // Fallback if chunks are empty but we have headlines
        if (chunk2.length === 0 && headlines.length > 0) chunk2 = headlines;
        if (chunk3.length === 0 && headlines.length > 0) chunk3 = headlines;

        populateBand(bands[0], chunk1);
        populateBand(bands[1], chunk2);
        populateBand(bands[2], chunk3);

    } catch (e) {
        console.error("Error loading ticker:", e);
    }
}

function scrollToPost(verificationId) {
    document.querySelector('[data-page="home"]').click();

    // Hide Hero
    const hero = document.querySelector('.hero');
    if (hero) hero.classList.add('hidden-smooth');

    setTimeout(() => {
        const post = document.getElementById(`post-${verificationId}`);
        if (post) {
            post.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Trigger click to expand if not expanded
            if (post.querySelector('.feed-details.hidden')) {
                post.click();
            }
            // Add temporary highlight
            post.style.transition = 'all 0.5s ease';
            post.style.borderColor = 'var(--accent-primary)';
            post.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.3)';
            post.style.transform = 'scale(1.02)';

            setTimeout(() => {
                post.style.borderColor = '';
                post.style.boxShadow = '';
                post.style.transform = '';
            }, 1500);
        } else {
            console.log("Post not found in current feed");
        }
    }, 100);
}

function displayPostInHero(item) {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    // Save original content if not saved
    if (!hero.dataset.originalContent) {
        hero.dataset.originalContent = hero.innerHTML;
    }

    // Ensure hero is visible
    hero.classList.remove('hidden-smooth');
    hero.style.display = 'block';

    // Check if current user owns this post or if it's a Reddit post
    const currentUserEmail = window.clerkAuth ? window.clerkAuth.getCurrentUserEmail() : null;
    const isOwnPost = currentUserEmail && item.user_email.toLowerCase() === currentUserEmail.toLowerCase();
    const isRedditPost = item.user_email && item.user_email.includes('@reddit');
    const showVoteButtons = !isOwnPost && !isRedditPost;

    // Create post content
    const content = `
        <div class="hero-post-display">
            <button onclick="restoreHero()" style="position: absolute; top: 1rem; right: 1rem; background: none; border: none; color: var(--text-secondary); font-size: 1.5rem; cursor: pointer; z-index: 10;">×</button>
            <div style="display: flex; align-items: flex-start; gap: 1.5rem; margin-bottom: 2rem;">
                <div class="verdict-badge ${item.verdict ? 'true' : 'false'}" style="width: 60px; height: 60px; font-size: 1.5rem; margin: 0; flex-shrink: 0;"></div>
                <div style="flex: 1;">
                    <h2 class="hero-headline">${item.headline || 'Verification Result'}</h2>
                    <div style="display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem;">
                        <span style="color: var(--text-secondary); font-size: 0.9rem;">by ${item.user_email.split('@')[0]} • ${new Date(item.created_at).toLocaleDateString()}</span>
                        
                        ${showVoteButtons ? `
                        <div class="hero-vote-buttons">
                            <button class="vote-btn upvote" onclick="handleHeroVote('${item.id}', 1, this)">
                                <span>▲</span> <span class="count">${item.upvotes || 0}</span>
                            </button>
                            <button class="vote-btn downvote" onclick="handleHeroVote('${item.id}', -1, this)">
                                <span>▼</span> <span class="count">${item.downvotes || 0}</span>
                            </button>
                        </div>
                        ` : `
                        <div style="color: var(--text-secondary); font-size: 0.85rem; font-style: italic;">
                            ${isRedditPost ? 'Reddit Post' : `${item.upvotes || 0} upvotes • ${item.downvotes || 0} downvotes`}
                        </div>
                        `}
                    </div>
                </div>
            </div>
            <div style="margin-bottom: 2rem; color: var(--text-primary); font-size: 1.1rem; line-height: 1.6; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                ${item.input_content}
            </div>
            <div class="feed-reasoning" style="margin-bottom: 1.5rem;">
                <h4 style="color: var(--accent-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🤖</span> AI Analysis
                </h4>
                <p style="line-height: 1.6; color: var(--text-secondary);">${item.reasoning}</p>
            </div>
            <div class="feed-claims">
                <h4 style="color: var(--accent-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>📌</span> Key Claims
                </h4>
                <ul style="padding-left: 1.5rem; color: var(--text-secondary); margin: 0;">
                    ${item.claims.map(c => `<li style="margin-bottom: 0.5rem;">${c}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;

    hero.innerHTML = content;
    hero.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

window.handleHeroVote = function (verificationId, voteType, btn) {
    const container = btn.closest('.hero-vote-buttons');
    const upBtn = container.querySelector('.upvote');
    const downBtn = container.querySelector('.downvote');
    handleVote(verificationId, voteType, upBtn, downBtn);
};

window.restoreHero = function () {
    const hero = document.querySelector('.hero');
    if (hero && hero.dataset.originalContent) {
        hero.innerHTML = hero.dataset.originalContent;
    }
};

// Eye Cursor Logic
document.addEventListener('mousemove', (e) => {
    const eye = document.getElementById('eye-cursor');
    if (eye) {
        eye.style.left = e.clientX + 'px';
        eye.style.top = e.clientY + 'px';
    }
});
