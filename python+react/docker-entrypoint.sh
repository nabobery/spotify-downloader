#!/bin/bash

# Activate virtual environment
source /app/backend/venv/bin/activate

# Start backend server in background
cd /app/backend
python app.py &

# Start frontend server
cd /app/frontend
npm install -g serve
serve -s dist -l 3000 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
