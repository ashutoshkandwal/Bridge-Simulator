# Quick Start: NOAA ENC Integration

## What You Need

NOAA ENC charts are **vector-based digital charts** that are much better than raster images. They contain:
- Coastlines (as lines/polygons)
- Depth contours
- Navigation aids (buoys, lights)
- Hazards and obstructions

## Step 1: Install GDAL (Critical)

GDAL is the key library for reading S-57 ENC files. You have two options:

### Option A: OSGeo4W (Recommended for Windows)

1. Download: https://trac.osgeo.org/osgeo4w/
2. Run installer `osgeo4w-setup.exe`
3. Select `Advanced Install`
4. Choose installation folder (default OK)
5. Under `Libs` tab, install:
   - `gdal` 
   - `gdal-python`
6. Click Next/Finish to complete
7. Verify in PowerShell:
   ```powershell
   python -c "from osgeo import ogr; print('GDAL OK')"
   ```

### Option B: Pip Install (Simpler but may require build tools)

```powershell
pip install gdal
pip install fiona shapely pyproj
```

If GDAL pip install fails, use Option A (OSGeo4W).

## Step 2: Download a Test Chart

1. Go to: https://www.charts.noaa.gov/ENCs/ENCs.shtml
2. Find your region (e.g., "Atlantic Coast - Mid-Atlantic")
3. Download a single chart (e.g., `US5VA18M` - Virginia area)
4. You'll get a `.zip` file containing `.000`, `.001` files
5. Extract and place in: `bridge_sim/areas/noaa_charts/`

Example structure:
```
bridge_sim/areas/noaa_charts/
  ├── US5VA18M.000
  ├── US5VA18M.001
  └── CATALOG.031
```

## Step 3: Test the Loader

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

Expected output:
```
[ENC] Opened: US5VA18M.000
[ENC] Layers available: 45
[ENC] Layer 0: LNDSRF (1234 features)
[ENC] Layer 1: DEPCNT (567 features)
...
[ENC] Bounds: lat=37.50..36.00, lon=-75.30..-74.50
[ENC] Exported ... features to chart_export.geojson
✓ ENC chart loaded and exported successfully!
```

## Step 4: Integration (In Progress)

Once GDAL is working, I'll add:
1. ECDIS method to load and render ENC layers as vectors
2. Coastline, depth contours, and navigation aids displayed
3. Proper symbology (colors/styles per NOAA standards)
4. Performance optimization for large charts

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'osgeo'` | Install GDAL via OSGeo4W (Option A above) |
| `No such file or directory` when opening chart | Verify chart file path; ensure you're in correct directory |
| "Failed to open chart" | Chart may be encrypted; download unencrypted S-57 from NOAA |
| Slow to load large chart | Normal for S-57; can pre-export to GeoJSON for faster loading |

## What NOAA Charts Include

| Feature | Layer Code | Example Uses |
|---------|-----------|--------------|
| Coastline | LNDSRF | Map boundaries |
| Depth Contours | DEPCNT | Navigation safety |
| Soundings | SOUNDG | Precise depth checks |
| Buoys/Markers | BOYINF | Navigation aids |
| Lights | LIGHTS | Night navigation |
| Wrecks | WRECK | Hazard avoidance |
| Traffic Lanes | TSEZNE | Separation schemes |

## Next: Try It

1. Complete Step 1 (install GDAL)
2. Complete Step 2 (download a chart)
3. Run Step 3 test
4. Let me know if it works!

---

Once you confirm GDAL works, I'll integrate ENC rendering into the ECDIS display.
