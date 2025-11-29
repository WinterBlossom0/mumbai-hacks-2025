# Truth Lens - Telegram Bot

AI-powered fact verification bot for Telegram with automatic announcement service.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Supabase account (for database)
- API keys for AI services

### Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**

Create/edit `.env` file in the project root with your API keys:
```env
# API Keys
OPENAI_API_KEY=your_openai_key
TAVALY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_ANNOUNCEMENT_CHANNEL_ID=your_channel_id_here  # Optional

# Bitly URL Shortener (Optional)
BITLY_ACCESS_TOKEN=your_bitly_access_token_here
```

3. **Set up Supabase database**
- Go to https://supabase.com and create a project
- Run the SQL from `../backend/database/setup_supabase.sql` in SQL Editor
- Copy your project URL and anon key to `.env`

4. **Run the bot**
```bash
python run_bot.py
```

## 📖 Features

### Core Features
- **Text Verification**: Send any text claim to verify
- **URL Verification**: Send article URLs for fact-checking
- **AI-Powered Analysis**: Uses Gemini 2.5 Pro for reasoning
- **Source Discovery**: Finds credible sources using Tavily API
- **Detailed Reports**: Provides verdict, reasoning, claims, and sources

### Announcement Service
- **Auto-Broadcasting**: Automatically announces fake news to a Telegram channel
- **Reddit Integration**: Monitors and announces fake Reddit posts
- **Configurable**: Enable/disable via environment variables

### Commands
- `/start` - Welcome message and instructions
- `/help` - Detailed help and usage tips

## 🏗️ Architecture

### Bot Components
```
telegram-bot/
├── bot/
│   ├── telegram_bot.py          # Main bot implementation
│   └── announcement_service.py  # Channel announcement service
├── run_bot.py                   # Bot runner script
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── BITLY_SETUP.md              # Bitly configuration guide
```

### How It Works

1. **User sends message** → Bot receives text or URL
2. **Claim Extraction** → Extracts key claims using AI
3. **Source Discovery** → Finds credible sources via Tavily
4. **Website Analysis** → Scrapes and analyzes source content
5. **AI Reasoning** → Gemini analyzes evidence and provides verdict
6. **Response** → Sends formatted result to user
7. **Database** → Saves verification to Supabase
8. **Announcement** (if enabled) → Posts fake news alerts to channel

## 🔧 Configuration

### Getting a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the token provided by BotFather
5. Add it to your `.env` file as `TELEGRAM_BOT_TOKEN`

### Setting Up Announcement Channel (Optional)

1. Create a Telegram channel
2. Add your bot as an administrator with posting permissions
3. Get the channel ID:
   - Forward a message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the channel ID (format: -100xxxxxxxxxx)
4. Add it to your `.env` file as `TELEGRAM_ANNOUNCEMENT_CHANNEL_ID`

### Bitly URL Shortening (Optional)

For cleaner source URLs in bot responses, set up Bitly:
- See [BITLY_SETUP.md](BITLY_SETUP.md) for detailed instructions

## 📊 Usage Examples

### Text Verification
```
User: The Earth is flat
Bot: ❌ VERDICT: FALSE
     📊 Analysis: This claim contradicts overwhelming scientific evidence...
     🔍 Key Claims: ...
     📚 Sources: 5
```

### URL Verification
```
User: https://example.com/article
Bot: 🔍 Analyzing your content...
     [Processes article and provides verdict]
```

## 🔍 Announcement Service

The announcement service automatically monitors for fake news and posts alerts to your configured channel.

### Features
- Polls database every 60 seconds
- Announces unannounced fake news from verifications
- Announces fake Reddit posts (if Reddit monitor is enabled)
- Handles rate limiting and retries
- Formats messages with emojis and markdown

### Message Format
```
🚨 FAKE NEWS ALERT 🚨
❌ VERDICT: FALSE

📰 Content: [Preview of fake content]
🔍 Why This is Fake: [AI reasoning]
📋 Key Claims: [List of claims]
📚 Verified Against X Sources
⏰ Detected: [Timestamp]
```

## 🛠️ Development

### Project Dependencies

The bot requires the following main packages:
- `python-telegram-bot>=20.7` - Telegram Bot API wrapper
- `openai>=1.0.0` - OpenAI API client
- `google-generativeai>=0.3.0` - Gemini API client
- `tavily-python>=0.3.0` - Tavily search API
- `supabase>=2.0.0` - Supabase database client
- `beautifulsoup4>=4.12.0` - Web scraping
- `requests>=2.31.0` - HTTP requests

### Backend Integration

The bot uses shared backend modules from `../backend/`:
- `main/claim_extractor.py` - Extract claims from text/URLs
- `main/claim_discoverer.py` - Discover credible sources
- `main/reasoning.py` - AI-powered fact-checking
- `database/supabase_client.py` - Database operations

## 🐛 Troubleshooting

### Bot doesn't respond
- Check if `TELEGRAM_BOT_TOKEN` is correct in `.env`
- Ensure the bot is running (`python run_bot.py`)
- Check logs for error messages

### "No claims could be extracted"
- Verify API keys are correct (OPENAI_API_KEY, GEMINI_API_KEY)
- Check if the content is too short or unclear
- Review logs for API errors

### Announcement service not working
- Ensure `TELEGRAM_ANNOUNCEMENT_CHANNEL_ID` is set
- Verify bot is admin in the channel with posting permissions
- Check channel ID format (-100xxxxxxxxxx)

### Bitly URLs not shortening
- See [BITLY_SETUP.md](BITLY_SETUP.md)
- Bot will fall back to truncated URLs if Bitly fails

## 📝 License

MIT License - Part of the Truth Lens project for Mumbai Hacks.
