# Twitter News Fetcher

This module fetches the latest news from Twitter using the **official Twitter API v2**.

## ✓ Free Tier Available!

Twitter API v2 offers a **FREE tier** that includes:
- 1,500 tweets per month
- Full tweet content and metadata
- Recent search (last 7 days)
- Perfect for this project!

## Quick Setup

### 1. Get Twitter API Access

Follow the detailed guide: [TWITTER_API_SETUP.md](./TWITTER_API_SETUP.md)

Quick steps:
1. Sign up at https://developer.twitter.com
2. Create a project and app
3. Get your Bearer Token
4. Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

### 2. Verify Setup

```bash
python backend/twitter/check_twitter_api.py
```

This will test your token and show if everything is working.

### 3. Run the Analysis

```bash
python backend/twitter/fetch_and_analyze.py
```

This will:
- Fetch latest tweets for #news
- Extract claims
- Discover sources
- Provide AI verdict

## Usage

### Standalone Script (Recommended)

```bash
python backend/twitter/fetch_and_analyze.py
```

### Programmatic Usage

```python
from twitter.news_fetcher import TwitterNewsFetcher

# Initialize the fetcher
fetcher = TwitterNewsFetcher()

# Fetch top 5 latest news tweets
tweets = fetcher.fetch_news(hashtag="news", max_items=5)

# Get combined text for analysis
long_text = fetcher.get_combined_text(tweets)

# Get tweet summaries
summaries = fetcher.get_tweet_summaries(tweets)
```

### Running the Test

```bash
python backend/test/test_twitter_long_text.py
```

## Features

- ✓ Uses official Twitter API v2
- ✓ FREE tier available (1,500 tweets/month)
- ✓ Fetches latest tweets for any hashtag
- ✓ Filters by language (default: English)
- ✓ Excludes retweets automatically
- ✓ Full tweet metadata (likes, retweets, author)
- ✓ Integrates with claim extraction pipeline

## Parameters

- `hashtag`: The hashtag to search (default: "news")
- `max_items`: Number of tweets to fetch (default: 5, max: 100)
- `language`: Tweet language filter (default: "en")

## Troubleshooting

### "TWITTER_BEARER_TOKEN not found"
Add your token to the `.env` file. See [TWITTER_API_SETUP.md](./TWITTER_API_SETUP.md)

### "Authentication failed"
Your token is invalid. Regenerate it in the Twitter Developer Portal.

### "Rate limit exceeded"
You've used your 1,500 tweets for the month. Wait until next month or upgrade.

### "No tweets found"
The hashtag might not have recent tweets. Try "breaking" or "update" instead.

## Files

- `news_fetcher.py` - Main Twitter fetcher class
- `fetch_and_analyze.py` - Standalone analysis script
- `check_twitter_api.py` - Setup verification tool
- `TWITTER_API_SETUP.md` - Detailed setup guide
- `README.md` - This file

## Why Twitter API v2?

- ✓ Official API (reliable and stable)
- ✓ FREE tier available
- ✓ No scraping issues
- ✓ Full tweet content
- ✓ Better rate limits than Apify free plan
- ✓ No paid subscription required for basic usage

## Next Steps

1. Complete setup using [TWITTER_API_SETUP.md](./TWITTER_API_SETUP.md)
2. Run `check_twitter_api.py` to verify
3. Start analyzing news with `fetch_and_analyze.py`
