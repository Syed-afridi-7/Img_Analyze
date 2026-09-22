@echo off
rem ============================================================
rem  EXIF Metadata Extractor - web frontend (self-contained)
rem  No Python installation required.
rem ============================================================
title EXIF Metadata Extractor - Web
cd /d "%~dp0"
echo Starting the EXIF Metadata Extractor web app...
echo Your browser will open at http://localhost:8501
echo (Keep this window open. Press Ctrl+C here to stop the app.)
echo.
python.exe -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
