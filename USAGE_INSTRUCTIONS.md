# Bridge Simulator Usage Instructions

## Quick Start

### 1. Start the Simulator
Double-click **`START_HEADLESS.bat`** or use the desktop shortcut.

A PowerShell window will open showing:
```
[RADAR WEB] Starting radar web server on http://127.0.0.1:5001/radar
[BG INTEGRATOR] Starting background thread...
[BG INTEGRATOR] ✓ Starting dead-reckoning loop...
[MAIN] ✓ Web RADAR (web menu) started - http://127.0.0.1:5001/
[MAIN] ✓ Web ECDIS started - http://127.0.0.1:5000/
[BG INTEGRATOR] State: LAT=0.00000, LON=0.00000, HDG=0.0°, SPD=0.0 kn
```

**IMPORTANT:** Leave this window open! Do NOT close it or press Ctrl+C.

### 2. Open the Menu
Open your web browser and go to:
```
http://127.0.0.1:5001/
```

### 3. Configure Scenario
Fill in the ship position and parameters:

**For Chesapeake Bay (US4MD20M chart):**
- **LAT**: `38.5`
- **LON**: `-76.3`
- **HDG**: `180` (heading South)
- **SPD**: `15` (15 knots)

**For targets:**
- **Target 1**: RNG: `5`, BRG: `45`, CRS: `270`, SPD: `10`
- **Target 2**: RNG: `8`, BRG: `180`, CRS: `0`, SPD: `12`

### 4. Start Simulation
Click the **"🚀 Start Simulator"** button.

The browser will automatically navigate to the ECDIS viewer.

### 5. Watch the Terminal
In the PowerShell window, you should now see:
```
[RADAR API] Initializing simulation with: {lat: 38.5, lon: -76.3, ...}
[RADAR API] ✓ Ship state initialized: LAT=38.5, LON=-76.3, HDG=180°, SPD=15 kn
[RADAR API] ✓ Target 1 created: RNG=5 NM, BRG=45°, CRS=270°, SPD=10 kn
[RADAR API] ✓ Target 2 created: RNG=8 NM, BRG=180°, CRS=0°, SPD=12 kn
[BG INTEGRATOR] State: LAT=38.50000, LON=-76.30000, HDG=180.0°, SPD=15.0 kn
[BG INTEGRATOR] DR update: LAT=38.49833, LON=-76.30000, HDG=180.0°, SPD=15.0 kn
```

### 6. View the Displays

**ECDIS (Chart Display):**
- Already open at `http://127.0.0.1:5000/`
- Ship marker moves on the chart in real-time
- Position updates via WebSocket

**Radar Display:**
- Open `http://127.0.0.1:5001/radar` in another tab
- Toggle **TM** (True Motion) mode to see ship movement
- Targets appear as yellow dots with trails

**Bridge Controls:**
- Open `http://127.0.0.1:5001/bridge_controls` 
- Change heading/speed in real-time

## Troubleshooting

### Ship Not Moving
**Symptom:** Background integrator shows `LAT=0.00000, LON=0.00000, SPD=0.0 kn`

**Cause:** Scenario not initialized

**Solution:** 
1. Go to `http://127.0.0.1:5001/`
2. Click "🚀 Start Simulator"
3. Check terminal for `[RADAR API] ✓ Ship state initialized` message

### Menu Shows "Stopped" After Returning
**Fixed:** Menu now uses sessionStorage to remember state during navigation

### Targets Not Visible on Radar
**Fixed:** Target coordinates now use absolute canvas positions centered at (300,300)

### Ship Position Changes But Not on Chart
**Cause:** WebSocket not connected or client not updating

**Solution:**
1. Refresh the ECDIS page
2. Check browser console for WebSocket errors
3. Verify `[WS] Client connected` appears in terminal

## Normal Operation

When running correctly, you'll see:
1. **Terminal logs** ship position every ~5 seconds
2. **ECDIS** shows ship marker moving smoothly on chart
3. **Radar TM mode** shows ship at center, targets moving
4. **Radar RM mode** shows ship stationary, targets moving relative to ship

## Stopping the Simulator

1. **Click "Exit Simulation"** in the menu, OR
2. **Close the PowerShell window**, OR
3. **Press Ctrl+C** in the PowerShell window

All web pages will stop updating when the simulator stops.

## Technical Notes

- **Background Integrator**: Runs at 5 Hz (every 0.2 seconds)
- **Dead Reckoning**: Updates ship lat/lon based on heading/speed
- **Target Motion**: Updates in pixel space, rotates for COURSE UP mode
- **WebSocket**: Real-time updates for ECDIS and radar
- **REST API**: Polling fallback for ship position

## Chart Coverage

Current chart: **US4MD20M** (Chesapeake Bay, Maryland)
- Latitude range: ~38.0° to 39.5° N
- Longitude range: ~-76.5° to -75.5° W

Ensure your ship position falls within these bounds!
