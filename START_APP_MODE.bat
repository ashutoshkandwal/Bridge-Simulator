@echo off
REM Launch browser in app window mode (minimal UI, no address bar/bookmarks)

REM Try Edge
start msedge --app="http://127.0.0.1:5001/"

REM Or try Chrome (uncomment below if Edge doesn't work)
REM start chrome --app="http://127.0.0.1:5001/"

echo.
echo Browser launched in app window mode
echo Use the fullscreen button (⛶) in the app to go fullscreen
pause
