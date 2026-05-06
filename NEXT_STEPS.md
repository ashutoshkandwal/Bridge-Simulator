# Next Steps — Copy/Paste Commands

After setup is complete, use these commands to test and integrate ENC support.

---

## 1. Verify Environment (After Each Shell Restart)

```powershell
# Check that gdal_env is active (should show (gdal_env) in prompt)
# If not:
conda activate gdal_env

# Verify GDAL and dependencies
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python test_enc_simple.py

# Expected output:
# ✓ GDAL 3.10.3 available
# ✓ Fiona available
# ✓ Shapely available
# ✓ ENC loader module available
```

---

## 2. Get a Test Chart

Visit: https://www.charts.noaa.gov/ENCs/ENCs.shtml

Download a S-57 chart (`.000` file). Popular test charts:
- **US5VA18M** (Chesapeake Bay) — good starting point
- **US4MD12M** (Mid-Atlantic coast)
- Any chart in your area of interest

Then:

```powershell
# Create chart directory
mkdir "bridge_sim\areas\noaa_charts"

# Copy downloaded chart here
# (e.g., move or copy US5VA18M.000 to bridge_sim/areas/noaa_charts/)
```

---

## 3. Test the ENC Loader (Verify Chart Loads)

```powershell
# From project root with gdal_env active
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"

# Expected output:
# [ENC] Opened: US5VA18M.000
# [ENC] Layers available: 14
# [ENC] Layer 0: M_CSCL (1 features)
# [ENC] Layer 1: M_COVR (5 features)
# ...
# [ENC] Bounds: lat=36.50..37.50, lon=-76.50..-76.50
# [ENC] Extracted N geometries from layer 'LNDSRF'
# [ENC] Extracted N geometries from layer 'DEPCNT'
# ...
# ✓ ENC chart loaded and exported successfully!
# 
# This creates: chart_export.geojson
```

---

## 4. Render in Simulator — Option A (Quick Standalone Test)

Create a new file: `test_run_with_enc.py`

```python
#!/usr/bin/env python3
"""Quick test: render ENC chart with moving ship."""

import pygame as pg
from bridge_sim.models import Ship
from bridge_sim.ecdis import ECDISDisplay

pg.init()
screen = pg.display.set_mode((1280, 800))
clock = pg.time.Clock()

# Ship starting position (adjust to your chart's region)
# For US5VA18M, use Chesapeake Bay coords:
ship = Ship(lat=37.0, lon=-76.0, heading=90, speed=10)

# Create ECDIS display
ecdis = ECDISDisplay(screen, ship=ship, follow_ship=False)

# Load ENC chart
chart_path = "bridge_sim/areas/noaa_charts/US5VA18M.000"
if ecdis.load_noaa_enc(chart_path):
    print("✓ ENC loaded and ready to render")
else:
    print("✗ Failed to load ENC; using fallback coastline")

# Render loop
running = True
dt = 0
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    # Update ship position
    ship.update_position(dt, north=0)
    
    # Clear and render
    screen.fill((0, 0, 0))
    ecdis.draw(ship)
    pg.display.set_caption(f"ENC Test — Ship: {ship.lat:.2f}N, {ship.lon:.2f}W")
    
    pg.display.flip()

pg.quit()
```

Then run:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python test_run_with_enc.py

# You should see:
# ✓ ENC loaded and ready to render
# Window opens with chart rendering
# Yellow circle (ship) appears on chart
# As time advances, ship moves across chart
# Close window to exit
```

---

## 5. Render in Simulator — Option B (Integrate into Main)

Edit: `bridge_sim/main.py`

Find the line where `ECDISDisplay` is created (around `_cycle_state` method):

```python
# EXISTING CODE:
ecdis = ECDISDisplay(self.screen, ship=ship, follow_ship=False)

# ADD AFTER (optional ENC loading):
enc_path = "bridge_sim/areas/noaa_charts/US5VA18M.000"
import os
if os.path.exists(enc_path):
    print(f"[MAIN] Loading ENC: {enc_path}")
    success = ecdis.load_noaa_enc(enc_path)
    if success:
        print("[MAIN] ✓ ENC loaded successfully")
else:
    print(f"[MAIN] ENC not found at {enc_path} (using PNG/fallback)")
```

Then run main simulator normally:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python -m bridge_sim.main

# or if that doesn't work:
python bridge_sim/main.py

# Navigate to ECDIS mode via menu
# Chart should render with ENC vector layers
```

---

## 6. Customize Rendering (Optional)

To change layer colors, edit: `bridge_sim/ecdis.py`

Find the `draw_enc_layers()` method and the `layer_colors` dict:

```python
layer_colors = {
    'LNDSRF': (100, 100, 80),      # Land (brownish) — change to e.g. (80, 120, 60)
    'DEPCNT': (150, 150, 200),     # Depth contours — change as desired
    'SLCONS': (100, 150, 180),
    'COALNE': (80, 120, 150),
    'BUOYS': (255, 200, 0),
    'LIGHTS': (255, 255, 100),
}
```

Colors are RGB tuples: `(red, green, blue)` where 0–255 is the intensity.

Save and re-run to see changes.

---

## 7. Export to GeoJSON (For Analysis/Visualization)

Already done automatically! When you load an ENC, a `chart_export.geojson` is created.

You can:

```powershell
# View in QGIS (free GIS software)
# View in online tool: https://geojson.io

# Or use in Python:
import json
with open('chart_export.geojson', 'r') as f:
    geojson = json.load(f)
    print(f"Total features: {len(geojson['features'])}")
    for feature in geojson['features'][:5]:
        print(f"  - {feature['properties'].get('layer', 'unknown')}")
```

---

## 8. Troubleshooting

### "ModuleNotFoundError: No module named 'osgeo'"
→ Forgot to activate gdal_env. Run: `conda activate gdal_env`

### "Failed to load ENC" or "Chart file not found"
→ Double-check the path:
```powershell
Test-Path "bridge_sim/areas/noaa_charts/US5VA18M.000"
# Should print: True
```

### Chart renders but no features visible
→ Verify layers loaded:
```powershell
# In test_run_with_enc.py, add after load_noaa_enc():
print(f"Loaded layers: {list(ecdis.enc_layers.keys())}")
# Should print: Loaded layers: ['LNDSRF', 'DEPCNT', ...]
```

### Performance is slow (many features to draw)
→ See "Performance Tips" in ENC_INTEGRATION_GUIDE.md

---

## 9. Next Project Ideas

Once basic ENC rendering works:

- [ ] Add layer toggle UI (show/hide coastlines, buoys, etc.)
- [ ] Add zoom controls to scale chart in/out
- [ ] Export rendered chart + ship to PNG/MP4
- [ ] Add depth info tooltips on hover
- [ ] Integrate tides/currents from NOAA API
- [ ] Add route planning UI
- [ ] Compare PNG chart vs ENC rendering quality

---

## Quick Reference

| Task | Command |
|------|---------|
| Activate environment | `conda activate gdal_env` |
| Verify setup | `python test_enc_simple.py` |
| Test ENC load | `python tools/noaa_enc_loader.py "path/to/chart.000"` |
| Run quick demo | `python test_run_with_enc.py` |
| Run main simulator | `python bridge_sim/main.py` |

---

## Files Created/Modified

**Created:**
- `test_enc_integration.py` – Full integration test
- `test_enc_simple.py` – Dependency verification
- `test_run_with_enc.py` – Quick demo (you create this)
- `ENC_INTEGRATION_GUIDE.md` – Comprehensive guide
- `ENC_QUICK_START.md` – Quick reference
- `SETUP_COMPLETE.md` – Setup summary
- `ARCHITECTURE.txt` – System architecture
- This file – `NEXT_STEPS.md`

**Modified:**
- `bridge_sim/ecdis.py` – Added `load_noaa_enc()` + `draw_enc_layers()`

---

## Support

For detailed documentation, see:
- **ENC_INTEGRATION_GUIDE.md** – Full API + troubleshooting
- **ARCHITECTURE.txt** – System design overview
- **ENC_QUICK_START.md** – One-page quick ref

Good luck! 🚀
