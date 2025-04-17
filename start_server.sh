#!/bin/bash

# Change to the application directory
cd "/Users/divyanshsingh/Desktop/project copy"

# Activate virtual environment
source venv/bin/activate

# Start gunicorn with logging to terminal
exec gunicorn --workers 1 --bind 0.0.0.0:5000 "app:create_app()" --log-level debug --access-logfile - --error-logfile - 