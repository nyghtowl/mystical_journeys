#!/bin/bash

# Mystical Journeys - Development Environment & Server
# This script sets up the environment and starts the development server

set -e  # Exit on any error

echo "🏰 Starting Mystical Journeys..."

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔮 Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if requirements.txt is newer than the last install
if [ ! -f ".venv/.last_install" ] || [ "requirements.txt" -nt ".venv/.last_install" ]; then
    echo "📦 Installing/updating dependencies..."
    pip install --upgrade pip > /dev/null
    pip install -r requirements.txt > /dev/null
    touch .venv/.last_install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file template..."
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "⚠️  Please edit .env and add your actual OpenAI API key"
fi

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is in use. Freeing it..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "🚀 Starting server at http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000