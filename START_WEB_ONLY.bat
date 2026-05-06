@echo off
echo Starting Maritime Bridge Simulator (Web Only - No PyGame Window)
echo ================================================================
echo.
echo Web Menu:     http://127.0.0.1:5001/
echo Web Radar:    http://127.0.0.1:5001/radar
echo Web ECDIS:    http://127.0.0.1:5000/
echo Bridge Ctrls: http://127.0.0.1:5001/bridge_controls
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

conda run -n gdal_env --no-capture-output python -m bridge_sim.main --headless

pause
