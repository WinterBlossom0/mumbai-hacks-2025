# Web Extension Backend

This is a dedicated backend server for the Truth Lens web extension. It runs independently from the main backend and provides the same misinformation detection capabilities.

## Features

- **Dedicated API Server**: Runs on port 8001 (separate from main backend on 8000)
- **Content Verification**: Verify text and URLs for misinformation
- **Claim Extraction**: Extract verifiable claims from content
- **Source Discovery**: Find credible sources using Tavily API
- **AI-Powered Reasoning**: Use OpenAI/Gemini to verify claims
- **Database Integration**: Store verification results in Supabase

## Quick Start

### 1. Install Dependencies

```bash
cd extension-backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file should already be configured with your API keys. If not, copy from the main `.env`:

```bash
cp ../.env .env
```

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for claim extraction and reasoning
- `GEMINI_API_KEY`: Google Gemini API key (fallback)
- `TAVALY_API_KEY`: Tavily API key for source discovery
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anonymous key

### 3. Run the Server

**Option 1: Using the dedicated runner script (from project root)**
```bash
# Web Extension Backend

This is a dedicated backend server for the Truth Lens web extension. It runs independently from the main backend and provides the same misinformation detection capabilities.

## Features

- **Dedicated API Server**: Runs on port 8001 (separate from main backend on 8000)
- **Content Verification**: Verify text and URLs for misinformation
- **Claim Extraction**: Extract verifiable claims from content
- **Source Discovery**: Find credible sources using Tavily API
- **AI-Powered Reasoning**: Use OpenAI/Gemini to verify claims
- **Database Integration**: Store verification results in Supabase

## Quick Start

### 1. Install Dependencies

```bash
cd extension-backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

The `.env` file should already be configured with your API keys. If not, copy from the main `.env`:

```bash
cp ../.env .env
```

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for claim extraction and reasoning
- `GEMINI_API_KEY`: Google Gemini API key (fallback)
- `TAVALY_API_KEY`: Tavily API key for source discovery
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anonymous key

### 3. Run the Server

**Option 1: Using the dedicated runner script (from project root)**
```bash
python run_extension_backend.py
```

**Option 2: Using uvicorn directly**
```bash
cd extension-backend
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

**Option 3: Run the app.py file**
```bash
cd extension-backend
python app.py
```

The server will start on `http://localhost:8001`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns: `{"status": "healthy"}`

### Test Connection
```
GET /test
```
Returns: `{"status": "ok", "message": "Extension API is working!"}`

### Verify Content
```
POST /api/verify
```

Request body:
```json
{
  "input_type": "text",  // or "url"
  "content": "Your content here",
  "user_id": "optional_user_id",
  "user_email": "optional_email"
}
```

Response:
```json
{
  "verification_id": "uuid",
  "verdict": true,  // true = credible, false = not credible
  "reasoning": "Detailed reasoning...",
  "claims": ["claim1", "claim2"],
  "sources": {"claim1": ["url1", "url2"]},
  "website_claims": {"url1": ["extracted_claim1"]}
}
```

## Web Extension Configuration

To connect the web extension to this backend:

1. Open the extension options page
2. Set the API endpoint to: `http://localhost:8001` (local) or your deployed URL
3. Save the settings

The extension will now use this dedicated backend for all verification requests.

## Architecture

This backend:
- **Shares core logic** with the main backend (imports from `backend/main`)
- **Runs independently** on a separate port
- **Uses the same database** (Supabase) for storing verifications
- **Provides the same API** as the main backend but optimized for extension use

## Troubleshooting

### Port Already in Use
If port 8001 is already in use, you can change it by:
1. Editing `app.py` and changing the port in `uvicorn.run()`
2. Updating the web extension's API endpoint in options

### API Key Errors
Make sure all required API keys are set in the `.env` file:
- Check OpenAI API key has sufficient quota
- Verify Tavily API key is valid
- Ensure Supabase credentials are correct

### CORS Errors
The backend is configured to allow all origins (`allow_origins=["*"]`). If you still see CORS errors:
- Check that the extension is making requests to the correct endpoint
- Verify the backend is running and accessible

## Development

To run in development mode with auto-reload:
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## Production Deployment

### Deploy to Render

The easiest way to deploy is using Render.com:

1. **See the detailed deployment guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Quick deploy**: 
   - Push your code to GitHub
   - Connect your repository to Render
   - Render will automatically detect `render.yaml` and deploy

**Deployment files included**:
- `render.yaml` - Render configuration
- `Procfile` - Process configuration
- `.python-version` - Python version specification

### Manual Deployment

For other platforms, use:
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Make sure to set all environment variables on your hosting platform.
