# Truth Lens - Chrome Extension

A Chrome extension that enables one-click fact-checking of news articles and web content using AI-powered verification.

## Features

- 🔍 **One-Click Verification** - Check any webpage for misinformation with a single click
- 🤖 **AI-Powered Analysis** - Uses advanced AI to extract claims and verify facts
- 📊 **Detailed Results** - See verdict, reasoning, claims, and credible sources
- 🎨 **Modern UI** - Beautiful dark theme with smooth animations
- ⚙️ **Customizable** - Configure API endpoint and preferences
- 🔔 **Notifications** - Get notified when verification is complete

## Installation

### Prerequisites

1. **Backend Running**: Make sure your Truth Lens FastAPI backend is running
   ```bash
   cd path/to/mum-hacks-misinfo
   python run.py
   ```
   The backend should be accessible at `http://localhost:8000`

### Install Extension (Chrome)

1. **Open Chrome Extensions Page**
   - Navigate to `chrome://extensions/`
   - Or click the three dots menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the Extension**
   - Click "Load unpacked"
   - Navigate to the `web-extension` folder in your project
   - Select the folder and click "Select Folder"

4. **Pin the Extension** (Optional)
   - Click the puzzle piece icon in Chrome toolbar
   - Find "Truth Lens - Fact Checker"
   - Click the pin icon to keep it visible

### Install Extension (Microsoft Edge)

1. **Open Edge Extensions Page**
   - Navigate to `edge://extensions/`
   - Or click the three dots menu → Extensions → Manage extensions

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the left sidebar or bottom left

3. **Load the Extension**
   - Click "Load unpacked"
   - Navigate to the `web-extension` folder in your project
   - Select the folder and click "Select Folder"

## Usage

### Basic Verification

1. **Navigate to a news article or webpage** you want to verify
2. **Click the Truth Lens extension icon** in your toolbar
3. **Click "Check This Page"** button
4. **Wait for analysis** - The extension will:
   - Extract content from the page
   - Send it to the backend for verification
   - Display results with verdict, reasoning, and sources

### Configure Settings

1. **Click the settings icon** (gear) in the extension popup
2. **Configure API Endpoint**:
   - Default: `http://localhost:8000`
   - Change if your backend runs on a different URL/port
3. **Set Preferences**:
   - Enable/disable desktop notifications
4. **Test Connection** to verify backend is accessible
5. **Save Settings**

## How It Works

```
┌─────────────┐
│  Web Page   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Content Script     │ ← Extracts article content
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Popup UI           │ ← User interface
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Background Worker  │ ← Handles API calls
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  FastAPI Backend    │ ← AI verification
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Results Display    │ ← Shows verdict & sources
└─────────────────────┘
```

## Troubleshooting

### Extension doesn't work

1. **Check backend is running**:
   ```bash
   curl http://localhost:8000/test
   ```
   Should return: `{"status":"ok","message":"API is working!"}`

2. **Check extension console**:
   - Right-click extension icon → Inspect popup
   - Look for errors in the Console tab

3. **Verify API endpoint**:
   - Open extension settings
   - Click "Test Connection"
   - Should show "Connection successful!"

### No content extracted

- The page might not have standard article structure
- Try a different news article or blog post
- Check browser console for errors (F12)

### API errors

- Ensure all API keys are set in backend `.env` file:
  - `OPENAI_API_KEY`
  - `TAVALY_API_KEY`
  - `GEMINI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`

### CORS errors

- The backend already has CORS enabled for all origins
- If you still see CORS errors, check your backend logs

## File Structure

```
web-extension/
├── manifest.json          # Extension configuration
├── popup.html            # Main popup UI
├── popup.css             # Popup styling
├── popup.js              # Popup logic
├── content.js            # Content extraction script
├── background.js         # Background service worker
├── options.html          # Settings page
├── options.js            # Settings logic
├── api.js                # API communication
├── utils.js              # Utility functions
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # This file
```

## API Endpoints Used

- `POST /api/verify` - Verify content
  ```json
  {
    "input_type": "text",
    "content": "Article text...",
    "user_id": "user_xxx",
    "user_email": "user@example.com"
  }
  ```

- `GET /test` - Test backend connection

## Development

### Debugging

1. **Popup debugging**:
   - Right-click extension icon → Inspect popup
   - Console shows popup.js logs

2. **Background worker debugging**:
   - Go to `chrome://extensions/`
   - Click "Inspect views: service worker"
   - Console shows background.js logs

3. **Content script debugging**:
   - Open any webpage
   - Press F12 → Console
   - Look for "Truth Lens content script loaded"

### Making Changes

1. Edit the files in `web-extension/` folder
2. Go to `chrome://extensions/`
3. Click the refresh icon on the Truth Lens extension
4. Test your changes

## Privacy & Data

- **User ID**: Generated locally, stored in browser
- **Verification Data**: Sent to your backend, stored in Supabase
- **No External Tracking**: All data stays within your infrastructure
- **API Keys**: Stored in backend, never exposed to extension

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs for errors
3. Check browser console for client-side errors

## License

MIT License - Part of the Truth Lens project for Mumbai Hacks
