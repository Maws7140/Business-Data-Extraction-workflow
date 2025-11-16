@echo off
REM Launch script for Business Data Extraction Web UI (Windows)

echo ==============================================
echo Business Data Extraction Tool - Web UI
echo ==============================================
echo.
echo Starting web interface...
echo The app will open in your browser automatically.
echo.
echo Press Ctrl+C to stop the server
echo ==============================================
echo.

streamlit run app.py
