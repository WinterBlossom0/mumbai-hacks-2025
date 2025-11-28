# Twitter News Fetcher - Quick Start

## ✅ What's Changed

Switched from **Apify** (paid only) to **Twitter API v2** (FREE tier available!)

## 🚀 Get Started in 3 Steps

### Step 1: Get Twitter API Access (5 minutes)

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign up for free account
3. Create a project and app
4. Copy your **Bearer Token**

**Detailed guide:** See [TWITTER_API_SETUP.md](./TWITTER_API_SETUP.md)

### Step 2: Add Token to .env

Open your `.env` file and replace:
```
TWITTER_BEARER_TOKEN=<YOUR_TWITTER_BEARER_TOKEN>
```

With your actual token:
```
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABcdefgh...
```

### Step 3: Test It

```bash
python backend/twitter/check_twitter_api.py
```

Should show: ✓ SUCCESS!

## 🎯 Run the Analysis

```bash
python backend/twitter/fetch_and_analyze.py
```

This will:
1. Fetch 5 latest tweets for #news
2. Extract claims from tweets
3. Discover sources for each claim
4. Analyze sources
5. Provide final verdict (TRUE/FALSE)

## 📊 What You Get (FREE)

- 1,500 tweets per month
- Full tweet content
- Author information
- Likes, retweets, replies
- Recent tweets (last 7 days)

**Perfect for your news analysis project!**

## 🔧 Files Created

- `news_fetcher.py` - Twitter API v2 integration
- `fetch_and_analyze.py` - Complete analysis pipeline
- `check_twitter_api.py` - Setup verification
- `TWITTER_API_SETUP.md` - Detailed setup guide
- `test_twitter_long_text.py` - Integration test

## ❓ Need Help?

Run the checker to diagnose issues:
```bash
python backend/twitter/check_twitter_api.py
```

See detailed setup: [TWITTER_API_SETUP.md](./TWITTER_API_SETUP.md)

## 🎉 Benefits Over Apify

| Feature | Apify Free | Twitter API v2 Free |
|---------|-----------|---------------------|
| Tweet content | ❌ No | ✓ Yes |
| Monthly limit | 10 items | 1,500 tweets |
| Cost | $0 (limited) | $0 (full access) |
| Setup time | 2 min | 5 min |
| Reliability | Medium | High (official) |

**Winner: Twitter API v2** 🏆
