#!/bin/bash

# Start script for VibeAgent on Render
echo "Starting VibeAgent Web Interface..."

# Set default port if not set (Render uses PORT environment variable)
export PORT=${PORT:-10000}

# Use Gunicorn for production if available, otherwise fall back to Flask dev server
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn (production server)..."
    gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 vibeagent.web_interface:app
else
    echo "Starting with Flask development server..."
    python -m vibeagent.web_interface
fi

