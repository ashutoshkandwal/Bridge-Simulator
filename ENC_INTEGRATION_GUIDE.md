# NOAA ENC Integration Guide

Your bridge simulator now has full NOAA S-57/S-101 Electronic Navigational Chart (ENC) support! This guide walks you through loading and rendering professional vector charts.

## What You Have

✅ **GDAL 3.10.3** – OGR library for reading S-57/S-101 files  
✅ **Fiona** – High-level OGR wrapper  
✅ **Shapely** – Geometry operations  
✅ **PyProj** – Coordinate transformations  
✅ **ENChart loader** (`tools/noaa_enc_loader.py`) – Extracts layers from ENC files  
✅ **ECDIS integration** (`bridge_sim/ecdis.py`) – Renders ENC layers on the display  

## Verification

To confirm everything is installed:

```powershell
# In gdal_env
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python test_enc_simple.py
```

Expected output:
```
✓ GDAL 3.10.3 available
✓ Fiona available
✓ Shapely available
✓ ENC loader module available
```

## Getting a Test Chart

1. Visit **https://www.charts.noaa.gov/ENCs/ENCs.shtml**
2. Download a **small S-57 chart** (`.000` file, ~5–20 MB)
   - Recommendation: Start with a chart near Gibraltar (test area) or your local area
   - Example: US5VA18M (Chesapeake Bay area) is a popular test chart
3. Create the chart directory:
   ```powershell
   mkdir "bridge_sim\areas\noaa_charts"
   ```
4. Copy the `.000` file there:
   ```powershell
   Copy-Item "C:\path\to\chart.000" "bridge_sim\areas\noaa_charts\"
   ```

## Testing the Loader

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

Expected output:
```
[ENC] Opened: US5VA18M.000
[ENC] Layers available: 14
[ENC] Layer 0: M_CSCL (1 features)
[ENC] Layer 1: M_COVR (5 features)
[ENC] Layer 2: M_QUAL (1 features)
...
[ENC] Bounds: lat=36.50..37.50, lon=-76.50..-75.50
[ENC] Extracted N geometries from layer 'LNDSRF'
...
✓ ENC chart loaded and exported successfully!
```

This creates a `chart_export.geojson` file with all chart geometries.

## Using in the Simulator

### Method 1: Quick Test (Python Script)

Create a test file `test_run_with_enc.py`:

```python
import pygame as pg
from bridge_sim.models import Ship
from bridge_sim.ecdis import ECDISDisplay

# Initialize Pygame
pg.init()
screen = pg.display.set_mode((1280, 800))
clock = pg.time.Clock()

# Create a ship at Chesapeake Bay (for US5VA18M test)
ship = Ship(lat=37.0, lon=-76.0, heading=90, speed=10)

# Create ECDIS display
ecdis = ECDISDisplay(screen, ship=ship, follow_ship=False)

# Load the ENC chart
chart_path = "bridge_sim/areas/noaa_charts/US5VA18M.000"
ecdis.load_noaa_enc(chart_path)

# Render loop
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    ship.update_position(0.016, north=0)  # ~60 FPS dt
    
    screen.fill((0, 0, 0))
    ecdis.draw(ship)
    pg.display.flip()
    clock.tick(60)

pg.quit()
```

Run it:
```powershell
python test_run_with_enc.py
```

### Method 2: Integrate into Main Simulator

Modify `bridge_sim/main.py` to optionally load an ENC:

```python
# In the ECDISDisplay initialization (around line where _cycle_state is defined):
ecdis = ECDISDisplay(screen, ship=ship, follow_ship=False)

# Try to load ENC if available
enc_path = "bridge_sim/areas/noaa_charts/US5VA18M.000"
if os.path.exists(enc_path):
    print(f"[MAIN] Loading ENC: {enc_path}")
    ecdis.load_noaa_enc(enc_path)
```

Then the main simulator will automatically render the ENC layers when you navigate to ECDIS mode.

## Available Layers

The ENC loader looks for these standard layers:

| Layer | Description | Color |
|-------|-------------|-------|
| **LNDSRF** | Land surfaces | Brown (100, 100, 80) |
| **DEPCNT** | Depth contours | Light blue (150, 150, 200) |
| **SLCONS** | Shoreline | Medium blue (100, 150, 180) |
| **COALNE** | Coastline | Dark blue (80, 120, 150) |
| **BUOYS** | Buoys | Yellow (255, 200, 0) |
| **LIGHTS** | Light structures | Bright yellow (255, 255, 100) |

Not all layers are present in every chart. The loader will report which layers were extracted.

## Rendering

The `draw_enc_layers()` method in `ECDISDisplay` converts Shapely geometries to Pygame primitives:

- **LineString** → `pg.draw.lines()` (coastlines, depth contours)
- **Polygon** → `pg.draw.polygon()` (land areas, restricted zones)
- **MultiLineString/MultiPolygon** → Individual line/polygon calls

Colors are defined per-layer for visual distinction. You can customize by editing the `layer_colors` dict in `draw_enc_layers()`.

## Performance Tips

- **Large charts**: ENCs can have thousands of geometries. If rendering is slow:
  - Load only specific layers: Edit `ENChart.get_layer()` call
  - Simplify geometries using Shapely: `geometry.simplify(tolerance=0.0001)`
  - Use display scale to reduce coordinate precision

- **Memory**: ENC files are small on disk but expand in memory. A large chart might use 50–200 MB after loading all geometries.

## Troubleshooting

### "ModuleNotFoundError: No module named 'osgeo'"
- Ensure you're running from within `gdal_env`:
  ```powershell
  conda activate gdal_env
  python test_enc_simple.py
  ```

### "GDAL_DATA is not defined" warnings
- Harmless. GDAL is looking for optional DXF support data. Doesn't affect chart loading.

### Chart not rendering
- Verify the file format: Should be S-57 (`.000`, `.001`, etc.) or S-101 (`.gpkg`)
- Check console output: `[ENC] Opened: ...` should appear
- Try the standalone loader first: `python tools/noaa_enc_loader.py <path>`

### Only grid visible, no ENC features
- Confirm layers were loaded: Check `[ENC] Layer X: ...` messages
- Verify `draw_enc_layers()` is called in `ecdis.draw()` (it is by default)
- Check color: Layers might be rendering in colors similar to the water background

## Next Steps

1. ✅ Download a test chart
2. ✅ Run `python tools/noaa_enc_loader.py <chart>`
3. ✅ Verify layers load and bounds print correctly
4. ✅ Create `test_run_with_enc.py` and render it
5. ✅ Integrate into main simulator or use as-is

## File Reference

- **`tools/noaa_enc_loader.py`** – ENChart class and layer extraction
- **`bridge_sim/ecdis.py`** – `load_noaa_enc()` and `draw_enc_layers()` methods
- **`test_enc_simple.py`** – Dependency verification script
- **`test_enc_integration.py`** – Full integration test (requires pygame)

---

Questions or issues? The ENC loader is designed to gracefully fall back if GDAL is unavailable, so your existing raster chart + PNG mode will continue to work even if ENC loading fails.
