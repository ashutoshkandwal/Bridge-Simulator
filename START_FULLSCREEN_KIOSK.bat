@echo off
echo ================================================
echo   Maritime Bridge Simulator - Full Launch
echo ================================================
echo.
echo Starting simulator backend...
echo.

REM Start the simulator in headless mode (background)
start /MIN "Bridge Simulator Backend" conda run -n gdal_env --no-capture-output python -m bridge_sim.main --headless

REM Wait for servers to initialize
echo Waiting for servers to start...
timeout /t 5 /nobreak >nul

echo.
echo Backend servers started!
echo Opening browser in fullscreen kiosk mode...
echo.

REM Launch browser in kiosk mode (fullscreen with no browser UI)
start msedge --kiosk "http://127.0.0.1:5001/" --edge-kiosk-type=fullscreen

REM Close this console window automatically after browser launches
timeout /t 2 /nobreak >nul
exit
