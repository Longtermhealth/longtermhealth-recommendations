#!/bin/bash
cd /home/site/wwwroot

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH to include the src directory
export PYTHONPATH=/home/site/wwwroot/src:$PYTHONPATH

# Start the application with gunicorn
# Note: We use --chdir src and app:app because app.py is in the src directory
gunicorn --bind 0.0.0.0:8000 --timeout 600 --access-logfile '-' --error-logfile '-' --chdir src app:app