#!/usr/bin/env python3
"""
Health check server to prevent Render free tier from sleeping.
Runs a simple Flask server on port 8080 that responds to /health requests.
"""

from flask import Flask
import threading
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint for keep-alive services."""
    return {'status': 'ok', 'message': 'Bot is running'}, 200

@app.route('/')
def index():
    """Root endpoint."""
    return {'service': 'Truth Lens Telegram Bot', 'status': 'active'}, 200

def run_health_server():
    """Run the Flask health server."""
    # Disable Flask's default logging to reduce noise
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

def start_health_server():
    """Start the health server in a background thread."""
    logger.info("Starting health check server on port 8080...")
    thread = threading.Thread(target=run_health_server, daemon=True)
    thread.start()
    logger.info("Health check server started successfully")
