# Deploying Extension Backend to Render

This guide will walk you through deploying the Truth Lens Extension Backend to Render.com.

## Prerequisites

- GitHub account (to connect your repository to Render)
- Render account (free tier is sufficient)
- Your repository pushed to GitHub

## Step 1: Prepare Your Repository

Make sure all the deployment files are committed and pushed to GitHub:

```bash
git add extension-backend/
git commit -m "Add extension backend with Render deployment config"
git push origin main
```

## Step 2: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** button
3. Select **"Web Service"**

## Step 3: Connect Your Repository

1. Click **"Connect a repository"**
2. If this is your first time, authorize Render to access your GitHub account
3. Find and select your repository: `mum-hacks-misinfo`
4. Click **"Connect"**

## Step 4: Configure the Web Service

Fill in the following details:

### Basic Settings

- **Name**: `truthlens-extension-backend` (or any name you prefer)
- **Region**: Choose the closest region (e.g., Oregon, Frankfurt, Singapore)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `extension-backend`
- **Runtime**: `Python 3`

### Build & Deploy Settings

- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```
  uvicorn app:app --host 0.0.0.0 --port $PORT
  ```

### Instance Type

- **Plan**: Select **"Free"** (or upgrade if needed)

## Step 5: Add Environment Variables

Click on **"Advanced"** and add the following environment variables:

| Key | Value | Where to Get It |
|-----|-------|-----------------|
| `PYTHON_VERSION` | `3.11.0` | Fixed value |
| `OPENAI_API_KEY` | `your-openai-key` | From your `.env` file |
| `TAVALY_API_KEY` | `your-tavaly-key` | From your `.env` file |
| `GEMINI_API_KEY` | `your-gemini-key` | From your `.env` file |
| `SUPABASE_URL` | `your-supabase-url` | From your `.env` file |
| `SUPABASE_KEY` | `your-supabase-key` | From your `.env` file |

**Important**: Copy the values from your local `extension-backend/.env` file.

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying your application
3. Wait for the deployment to complete (usually 2-5 minutes)

## Step 7: Get Your Deployment URL

Once deployed, Render will provide you with a URL like:
```
https://truthlens-extension-backend.onrender.com
```

## Step 8: Update Your Web Extension

Update the web extension to use the deployed backend:

1. Open `web-extension/options.html` in your extension
2. Go to the extension options page
3. Change the API endpoint from `http://localhost:8001` to your Render URL:
   ```
   https://truthlens-extension-backend.onrender.com
   ```
4. Click "Save Settings"
5. Click "Test Connection" to verify it works

## Step 9: Test the Deployment

Test your deployed backend:

### Test Health Endpoint
```bash
curl https://truthlens-extension-backend.onrender.com/api/health
```

Expected response:
```json
{"status":"healthy"}
```

### Test Connection Endpoint
```bash
curl https://truthlens-extension-backend.onrender.com/test
```

Expected response:
```json
{"status":"ok","message":"Extension API is working!"}
```

## Important Notes

### Free Tier Limitations

- **Spin Down**: Free tier services spin down after 15 minutes of inactivity
- **Spin Up Time**: First request after spin down takes 30-60 seconds
- **Monthly Hours**: 750 hours per month (enough for continuous operation)

### Keeping the Service Alive

If you want to prevent spin down, you can:

1. **Upgrade to a paid plan** ($7/month for Starter plan)
2. **Use a cron job** to ping the health endpoint every 10 minutes:
   ```bash
   */10 * * * * curl https://truthlens-extension-backend.onrender.com/api/health
   ```

### CORS Configuration

The extension backend is already configured to allow all origins:
```python
allow_origins=["*"]
```

This is necessary for browser extensions to work. In production, you might want to restrict this.

## Troubleshooting

### Build Fails

**Problem**: Build command fails

**Solution**: 
- Check that `requirements.txt` is in the `extension-backend/` directory
- Verify Python version is set to 3.11.0
- Check build logs for specific errors

### Import Errors

**Problem**: `ModuleNotFoundError` for backend modules

**Solution**:
- Ensure the repository structure is correct
- The `backend/` directory should be at the root level
- The `extension-backend/` directory should also be at root level

### Environment Variables Not Working

**Problem**: API keys not being read

**Solution**:
- Double-check all environment variables are set in Render dashboard
- Make sure there are no extra spaces in the values
- Restart the service after adding variables

### Service Won't Start

**Problem**: Service fails to start

**Solution**:
- Check the logs in Render dashboard
- Verify the start command is correct: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Make sure `app.py` exists in `extension-backend/`

## Monitoring Your Deployment

### View Logs

1. Go to your service in Render dashboard
2. Click on **"Logs"** tab
3. You'll see real-time logs with `[EXTENSION]` prefixes

### Check Metrics

1. Click on **"Metrics"** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

## Updating Your Deployment

Whenever you make changes to the extension backend:

1. Commit and push changes to GitHub:
   ```bash
   git add extension-backend/
   git commit -m "Update extension backend"
   git push origin main
   ```

2. Render will automatically detect the changes and redeploy

3. You can also manually trigger a deploy from the Render dashboard

## Alternative: Using render.yaml

If you prefer infrastructure-as-code, you can use the `render.yaml` file:

1. In Render dashboard, go to **"Blueprint"**
2. Click **"New Blueprint Instance"**
3. Connect your repository
4. Render will automatically detect `extension-backend/render.yaml`
5. Click **"Apply"**

This will create the service with all settings pre-configured.

## Cost Optimization

### Free Tier Strategy

- Use the free tier for development and testing
- The 750 hours/month is enough for continuous operation
- Spin down is acceptable for most use cases

### Paid Tier Benefits ($7/month)

- No spin down
- Faster response times
- More resources (512 MB RAM → 2 GB RAM)
- Better for production use

## Security Best Practices

1. **Never commit `.env` files** to GitHub
2. **Use Render's environment variables** for secrets
3. **Rotate API keys** regularly
4. **Monitor usage** to detect unusual activity
5. **Set up alerts** for errors and high usage

## Next Steps

After successful deployment:

1. ✅ Test all endpoints thoroughly
2. ✅ Update web extension with production URL
3. ✅ Test the extension with real content
4. ✅ Monitor logs for any errors
5. ✅ Set up error tracking (optional)

## Support

If you encounter issues:

1. Check Render's [documentation](https://render.com/docs)
2. Review the [deployment logs](https://dashboard.render.com)
3. Check the [Render community forum](https://community.render.com)

---

**Congratulations!** Your extension backend is now deployed and accessible worldwide! 🎉
