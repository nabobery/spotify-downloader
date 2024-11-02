#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
BACKEND_PATH="./backend"
FRONTEND_PATH="./frontend"
VENV_PATH="$BACKEND_PATH/venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to start backend
start_backend() {
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${RED}Virtual environment not found at $VENV_PATH${NC}"
        echo -e "${YELLOW}Create one using: python -m venv backend/venv${NC}"
        return 1
    fi

    # Start backend server
    echo -e "${GREEN}Starting backend server...${NC}"
    # Using Git Bash's start command for Windows
    start "Backend Server" bash -c "source $VENV_PATH/Scripts/activate && cd $BACKEND_PATH && export PYTHONPATH=$BACKEND_PATH && python app.py"

    return 0
}

# Function to start frontend
start_frontend() {
    # Check if package.json exists
    if [ ! -f "$FRONTEND_PATH/package.json" ]; then
        echo -e "${RED}Frontend package.json not found${NC}"
        return 1
    fi

    # Start frontend server
    echo -e "${GREEN}Starting frontend server...${NC}"
    # Using Git Bash's start command for Windows
    start "Frontend Server" bash -c "cd $FRONTEND_PATH && npm run dev"

    return 0
}

# Parse command line arguments
NO_BACKEND=false
NO_FRONTEND=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-backend)
            NO_BACKEND=true
            shift
            ;;
        --no-frontend)
            NO_FRONTEND=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check for required commands
if ! command_exists python; then
    echo -e "${RED}Python is not installed or not in PATH${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}NPM is not installed or not in PATH${NC}"
    exit 1
fi

# Start servers
BACKEND_STARTED=0
FRONTEND_STARTED=0

if [ "$NO_BACKEND" = false ]; then
    start_backend
    BACKEND_STARTED=$?
    if [ $BACKEND_STARTED -eq 0 ]; then
        echo -e "${GREEN}Backend server started successfully${NC}"
    fi
fi

if [ "$NO_FRONTEND" = false ]; then
    start_frontend
    FRONTEND_STARTED=$?
    if [ $FRONTEND_STARTED -eq 0 ]; then
        echo -e "${GREEN}Frontend server started successfully${NC}"
    fi
fi

# Show summary
if [ $BACKEND_STARTED -eq 0 ] && [ $FRONTEND_STARTED -eq 0 ]; then
    echo -e "${GREEN}Development environment started successfully!${NC}"
    echo -e "${YELLOW}Note: Server windows have been opened in separate windows.${NC}"
else
    echo -e "${YELLOW}Some services failed to start.${NC}"
    exit 1
fi
