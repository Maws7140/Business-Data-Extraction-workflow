#!/bin/bash

# Firecrawl LLM Extraction - Web UI Startup Script

echo "🚀 Starting Firecrawl LLM Extraction Web UI..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit .env and add your API keys before using the application."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed."
fi

# Start the server
echo ""
echo "🌐 Starting web server on http://localhost:8000"
echo "📝 Press CTRL+C to stop"
echo ""

python -m src.cli.main serve
