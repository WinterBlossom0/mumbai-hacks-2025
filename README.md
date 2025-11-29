# Truth Lens 🔍

**AI-Powered Misinformation Detection Platform**

Truth Lens is a comprehensive multi-platform ecosystem designed to combat misinformation through AI-powered fact-checking and verification. Built for Mumbai Hacks, this project provides real-time content verification across web, mobile, browser extensions, and Telegram.

---

## 🌐 Live Deployments

### Glass Branch
- **Frontend (Web App)**: [https://voidtruth-frontend.onrender.com/](https://voidtruth-frontend.onrender.com/)
- **Backend API**: [https://voidtruth.onrender.com/](https://voidtruth.onrender.com/)

### Ecosystem Branch
- **Web Extension Backend**: [https://truthlens-web-extension-backend.onrender.com](https://truthlens-web-extension-backend.onrender.com)
- **Telegram Bot**: [https://truthlens-telegram-bot.onrender.com](https://truthlens-telegram-bot.onrender.com)

---

## ✨ Features

### Core Capabilities
- **Multi-Source Verification**: Verify text content and URLs against credible sources
- **AI-Powered Analysis**: Leverages OpenAI GPT-4 and Google Gemini 2.5 Pro for intelligent reasoning
- **Claim Extraction**: Automatically extracts verifiable claims from content
- **Source Discovery**: Uses Tavily API to find and analyze credible sources
- **Real-Time Detection**: Instant verification with detailed reasoning and evidence
- **Cross-Platform**: Available on web, mobile, browser extension, and Telegram

### Platform-Specific Features
- **Web App**: Modern Next.js interface with authentication and user history
- **Mobile App**: Native Flutter application with offline support
- **Browser Extension**: One-click verification for any webpage (Chrome/Edge)
- **Telegram Bot**: Conversational fact-checking with automatic fake news alerts
- **Reddit Monitor**: Tracks and verifies Reddit posts for misinformation

---

## 🏗️ Architecture

```
Truth Lens Ecosystem
│
├── Frontend (Next.js + TypeScript)
│   ├── Modern glassmorphism UI
│   ├── Clerk authentication
│   ├── Real-time verification
│   └── User history & feed
│
├── Backend (FastAPI + Python)
│   ├── Main API (Port 8000)
│   ├── Mobile API (Port 8001)
│   ├── Extension API (Port 8001)
│   └── Shared verification logic
│
├── Web Extension (Chrome/Edge)
│   ├── Content extraction
│   ├── One-click verification
│   └── Popup interface
│
├── Telegram Bot
│   ├── Conversational interface
│   ├── Auto-announcement service
│   └── Channel broadcasting
│
├── Mobile App (Flutter)
│   ├── Native iOS/Android
│   ├── Offline support
│   └── Push notifications
│
└── Database (Supabase)
    ├── PostgreSQL
    ├── Real-time subscriptions
    └── User management
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- Supabase account
- API keys (OpenAI, Gemini, Tavily)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd truth-lens
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
# AI APIs
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
TAVALY_API_KEY=your_tavily_key

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ANNOUNCEMENT_CHANNEL_ID=your_channel_id

# Reddit (Optional)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent

# URL Shortener (Optional)
BITLY_ACCESS_TOKEN=your_bitly_token
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**Extension Backend:**
```bash
cd extension-backend
pip install -r requirements.txt
```

**Telegram Bot:**
```bash
cd telegram-bot
pip install -r requirements.txt
```

### 4. Set Up Database
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Run the SQL schema from `backend/database/setup_supabase.sql`
3. Copy your project URL and anon key to `.env`

### 5. Run the Services

**Main Backend:**
```bash
python run.py
# Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

**Extension Backend:**
```bash
python run_extension_backend.py
# Runs on http://localhost:8001
```

**Telegram Bot:**
```bash
python run_telegram_bot.py
```

---

## 📱 Platform Guides

### Web Application
The Next.js frontend provides a modern, responsive interface for content verification.

**Features:**
- User authentication with Clerk
- Real-time verification
- Public feed of verified content
- Personal verification history
- Responsive glassmorphism design

**Tech Stack:**
- Next.js 14
- TypeScript
- Tailwind CSS
- Framer Motion
- Clerk Auth

**Local Development:**
```bash
cd frontend
npm run dev
```

### Browser Extension
Chrome/Edge extension for one-click webpage verification.

**Installation:**
1. Navigate to `chrome://extensions/` (Chrome) or `edge://extensions/` (Edge)
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `web-extension` folder

**Usage:**
1. Click the Truth Lens icon in your toolbar
2. Click "Check This Page"
3. View verification results with sources

**Configuration:**
- Open extension settings (gear icon)
- Set API endpoint (default: `http://localhost:8001`)
- Test connection and save

See [web-extension/README.md](web-extension/README.md) for details.

### Telegram Bot
Conversational fact-checking bot with automatic fake news alerts.

**Setup:**
1. Get bot token from [@BotFather](https://t.me/botfather)
2. Add token to `.env` as `TELEGRAM_BOT_TOKEN`
3. Run: `python run_telegram_bot.py`

**Commands:**
- `/start` - Welcome message
- `/help` - Usage instructions
- Send any text or URL to verify

**Announcement Service:**
- Automatically broadcasts fake news alerts to a channel
- Configure channel ID in `.env`
- Polls database every 60 seconds

See [telegram-bot/README.md](telegram-bot/README.md) for details.

### Mobile App
Native Flutter application for iOS and Android.

**Features:**
- Native performance
- Offline support
- Push notifications
- Material Design 3

**Setup:**
```bash
cd mobile_app
flutter pub get
flutter run
```

See [backend_mobile/README.md](backend_mobile/README.md) for API details.

---

## 🔧 API Documentation

### Main Backend Endpoints

**Base URL:** `https://voidtruth.onrender.com` (Production) or `http://localhost:8000` (Local)

#### Verify Content
```http
POST /api/verify
Content-Type: application/json

{
  "input_type": "text",  // or "url"
  "content": "Content to verify",
  "user_id": "optional_user_id",
  "user_email": "optional_email"
}
```

**Response:**
```json
{
  "verification_id": "uuid",
  "verdict": true,
  "reasoning": "Detailed analysis...",
  "claims": ["claim1", "claim2"],
  "sources": {
    "claim1": ["url1", "url2"]
  },
  "website_claims": {
    "url1": ["extracted_claim"]
  }
}
```

#### Get Public Feed
```http
GET /api/feed?limit=20&offset=0
```

#### Get User History
```http
GET /api/history/{user_id}?limit=50
```

#### Health Check
```http
GET /test
```

### Interactive Documentation
- **Swagger UI**: [https://voidtruth.onrender.com/docs](https://voidtruth.onrender.com/docs)
- **ReDoc**: [https://voidtruth.onrender.com/redoc](https://voidtruth.onrender.com/redoc)

---

## 🧠 How It Works

### Verification Pipeline

1. **Input Processing**
   - Accepts text or URL
   - Extracts content from URLs using BeautifulSoup
   - Normalizes and cleans input

2. **Claim Extraction**
   - Uses OpenAI GPT-4 to identify verifiable claims
   - Filters out opinions and subjective statements
   - Returns structured list of factual claims

3. **Source Discovery**
   - Queries Tavily API for each claim
   - Finds credible sources (news, academic, government)
   - Scrapes and extracts content from sources

4. **Evidence Analysis**
   - Compares claims against source content
   - Extracts supporting/contradicting evidence
   - Builds comprehensive evidence base

5. **AI Reasoning**
   - Google Gemini 2.5 Pro analyzes all evidence
   - Provides verdict (TRUE/FALSE/MIXED)
   - Generates detailed reasoning
   - Cites specific sources

6. **Storage & Response**
   - Saves verification to Supabase
   - Returns formatted result to user
   - Triggers announcements if fake news detected

---

## 🗂️ Project Structure

```
truth-lens/
├── backend/                    # Main FastAPI backend
│   ├── api/                   # API routes
│   ├── database/              # Supabase client & schemas
│   ├── main/                  # Core verification logic
│   │   ├── claim_extractor.py
│   │   ├── claim_discoverer.py
│   │   └── reasoning.py
│   ├── reddit/                # Reddit monitoring
│   └── requirements.txt
│
├── frontend/                   # Next.js web application
│   ├── src/
│   │   ├── app/              # App router pages
│   │   └── components/       # React components
│   ├── public/               # Static assets
│   └── package.json
│
├── extension-backend/          # Dedicated extension API
│   ├── app.py                # FastAPI app
│   ├── render.yaml           # Render deployment config
│   └── requirements.txt
│
├── web-extension/             # Chrome/Edge extension
│   ├── manifest.json         # Extension config
│   ├── popup.html/js/css     # Popup interface
│   ├── content.js            # Content extraction
│   ├── background.js         # Service worker
│   └── options.html/js       # Settings page
│
├── telegram-bot/              # Telegram bot
│   ├── bot/
│   │   ├── telegram_bot.py   # Bot implementation
│   │   └── announcement_service.py
│   ├── run_bot.py            # Bot runner
│   └── requirements.txt
│
├── mobile_app/                # Flutter mobile app
│   └── (Flutter project structure)
│
├── backend_mobile/            # Mobile-optimized API
│   ├── api/
│   └── requirements.txt
│
├── run.py                     # Main backend runner
├── run_extension_backend.py   # Extension backend runner
├── run_telegram_bot.py        # Telegram bot runner
└── .env                       # Environment variables
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Models**: OpenAI GPT-4, Google Gemini 2.5 Pro
- **Search**: Tavily API
- **Database**: Supabase (PostgreSQL)
- **Web Scraping**: BeautifulSoup4, Requests
- **Reddit**: PRAW (Python Reddit API Wrapper)

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Auth**: Clerk
- **Icons**: Lucide React

### Browser Extension
- **Manifest**: V3
- **APIs**: Chrome Extension APIs
- **UI**: Vanilla JavaScript + CSS

### Mobile
- **Framework**: Flutter
- **Language**: Dart
- **State Management**: Provider/Riverpod

### Telegram Bot
- **Library**: python-telegram-bot
- **Async**: asyncio

### Infrastructure
- **Hosting**: Render.com
- **Database**: Supabase Cloud
- **Version Control**: Git

---

## 🚢 Deployment

### Frontend (Render)
1. Connect GitHub repository
2. Select `frontend` folder
3. Build command: `npm install && npm run build`
4. Start command: `npm start`
5. Environment: Node.js

### Backend (Render)
1. Connect GitHub repository
2. Select `backend` or `extension-backend` folder
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

### Telegram Bot (Render)
1. Uses `render.yaml` for configuration
2. Runs as background worker
3. Health check server on port 10000
4. Auto-deploys from ecosystem branch

See individual README files for detailed deployment instructions.

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest test/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
1. **Test Backend**: `curl http://localhost:8000/test`
2. **Test Extension Backend**: `curl http://localhost:8001/api/health`
3. **Test Verification**: Use Swagger UI at `/docs`

---

## 🔐 Security & Privacy

- **API Keys**: Stored securely in environment variables
- **User Data**: Encrypted in Supabase
- **Authentication**: Clerk provides secure auth
- **CORS**: Configured for specific origins
- **Rate Limiting**: Implemented on API endpoints
- **Data Retention**: Configurable retention policies

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Mumbai Hacks** - For the opportunity to build this project
- **OpenAI** - GPT-4 API for claim extraction
- **Google** - Gemini 2.5 Pro for reasoning
- **Tavily** - Search API for source discovery
- **Supabase** - Database and authentication
- **Render** - Hosting and deployment

---

## 📧 Contact & Support

For questions, issues, or feedback:
- Open an issue on GitHub
- Check existing documentation in component READMEs
- Review API documentation at `/docs` endpoints

---

## 🗺️ Roadmap

### Current Features
- ✅ Multi-platform verification (Web, Mobile, Extension, Telegram)
- ✅ AI-powered claim extraction and reasoning
- ✅ Source discovery and analysis
- ✅ User authentication and history
- ✅ Public feed and social features
- ✅ Reddit monitoring
- ✅ Telegram announcements

### Planned Features
- 🔄 Real-time collaborative fact-checking
- 🔄 Browser extension for Firefox and Safari
- 🔄 Advanced analytics dashboard
- 🔄 API rate limiting and quotas
- 🔄 Multi-language support
- 🔄 Video and audio content verification
- 🔄 Community voting and reputation system
- 🔄 Integration with fact-checking organizations

---

## 📊 Project Stats

- **Platforms**: 4 (Web, Mobile, Extension, Telegram)
- **API Endpoints**: 15+
- **AI Models**: 2 (GPT-4, Gemini 2.5 Pro)
- **Languages**: Python, TypeScript, JavaScript, Dart
- **Lines of Code**: 10,000+

---

**Built with ❤️ for Mumbai Hacks**

*Fighting misinformation, one verification at a time.*
