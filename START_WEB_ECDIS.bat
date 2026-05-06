@echo off
echo Starting Web ECDIS Viewer...
echo.
echo This will:
echo 1. Start the Flask server
echo 2. Load the ENC chart (US4MD20M)
echo 3. Show a demo ship moving in a circle
echo.
echo Open http://127.0.0.1:5000 in your browser to view
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0web"
call conda run -n gdal_env python server.py

pause
