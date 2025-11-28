# Twitter API v2 Setup Guide

## Step 1: Create Twitter Developer Account

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Sign in with your Twitter account
3. Click "Sign up for Free Account"
4. Fill out the application form:
   - Account name: Your name or project name
   - Use case: Select "Making a bot" or "Exploring the API"
   - Description: "Building a news analysis tool to verify claims"

## Step 2: Create a Project and App

1. Once approved, go to the Developer Portal
2. Click "Create Project"
3. Give it a name (e.g., "News Analyzer")
4. Select use case: "Making a bot" or "Exploring the API"
5. Provide a description
6. Create an App within the project

## Step 3: Get Your Bearer Token

1. In your App settings, go to "Keys and tokens"
2. Under "Authentication Tokens", find "Bearer Token"
3. Click "Generate" if not already generated
4. **COPY THIS TOKEN** - you won't see it again!

## Step 4: Add Token to .env File

Open your `.env` file and add:

```
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```

Replace `<YOUR_TWITTER_BEARER_TOKEN>` with the actual token you copied.

## Step 5: Test Your Setup

Run the checker script:

```bash
python backend/twitter/check_twitter_api.py
```

This will verify your token is working correctly.

## Free Tier Limits

Twitter API v2 Free tier includes:
- ✓ 1,500 tweets per month
- ✓ Recent search (last 7 days)
- ✓ Full tweet content
- ✓ User information
- ✓ Public metrics (likes, retweets)

**This is perfect for your use case!**

## Usage

Once set up, run:

```bash
python backend/twitter/fetch_and_analyze.py
```

Or run the test:

```bash
python backend/test/test_twitter_long_text.py
```

## Troubleshooting

### "TWITTER_BEARER_TOKEN not found"
- Make sure you added it to the `.env` file
- Check there are no extra spaces or quotes

### "Authentication failed"
- Your token might be invalid
- Regenerate it in the Twitter Developer Portal

### "Rate limit exceeded"
- You've used your 1,500 tweets for the month
- Wait until next month or upgrade to paid tier

### "No tweets found"
- The hashtag might not have recent tweets
- Try a different hashtag like "breaking" or "update"

## Next Steps

After setup, you can:
1. Fetch tweets for any hashtag
2. Extract claims automatically
3. Discover sources
4. Get AI-powered verdicts

All for FREE with the Twitter API v2 free tier!
