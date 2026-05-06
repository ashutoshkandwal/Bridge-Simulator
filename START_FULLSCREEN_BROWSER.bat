@echo off
REM Launch Chrome/Edge in kiosk mode (fullscreen app mode)
REM Automatically hides address bar, bookmarks, and all browser UI

REM Try Edge first (most Windows systems)
start msedge --kiosk "http://127.0.0.1:5001/" --edge-kiosk-type=fullscreen

REM If Edge doesn't work, try Chrome
REM start chrome --kiosk "http://127.0.0.1:5001/" --kiosk-fullscreen

echo.
echo Browser launched in kiosk mode
echo Press Alt+F4 to exit kiosk mode
pause
