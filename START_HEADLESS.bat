@echo off
REM Start Bridge Simulator in Headless Mode
REM This runs the simulator without a GUI window, accessible via web browser at:
REM   Main Menu: http://127.0.0.1:5001/
REM   ECDIS:     http://127.0.0.1:5000/
REM   Radar:     http://127.0.0.1:5001/radar

TITLE Bridge Simulator - Headless Mode

echo ========================================
echo   BRIDGE SIMULATOR - HEADLESS MODE
echo ========================================
echo.
echo Starting web servers...
echo Main Menu: http://127.0.0.1:5001/
echo ECDIS:     http://127.0.0.1:5000/
echo Radar:     http://127.0.0.1:5001/radar
echo.
echo Press Ctrl+C to stop the simulator
echo ========================================
echo.

REM Run in headless mode (--headless is the default now, but explicit is clearer)
call conda run -n gdal_env --no-capture-output python -m bridge_sim.main --headless

pause
