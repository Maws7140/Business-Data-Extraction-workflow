@echo off
REM Firecrawl LLM Extraction - Web UI Startup Script (Windows)

echo Starting Firecrawl LLM Extraction Web UI...
echo.

REM Check if .env exists
if not exist .env (
    echo Warning: .env file not found. Copying from .env.example...
    copy .env.example .env
    echo Please edit .env and add your API keys before using the application.
    echo.
)

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed.
)

REM Start the server
echo.
echo Starting web server on http://localhost:8000
echo Press CTRL+C to stop
echo.

python -m src.cli.main serve
