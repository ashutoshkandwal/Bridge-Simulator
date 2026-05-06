# NOAA ENC Integration Guide

This document describes how to integrate NOAA Electronic Navigational Charts (ENC) into the bridge simulator.

## What is NOAA ENC?

**NOAA ENC** (Electronic Navigational Chart) is a standardized digital chart format used by mariners worldwide. It uses the **S-57** standard (and newer S-101) with vector layers for:
- Coastlines and land masses
- Depth contours and bathymetry
- Navigation aids (buoys, lights, markers)
- Obstructions and hazards
- Traffic separation schemes

**Sources:**
- Download free charts: https://www.charts.noaa.gov/ENCs/ENCs.shtml
- Format: S-57 (`.000` files) or S-101 (GeoPackage `.gpkg`)
- Coverage: All US coastal waters

## Prerequisites & Setup

### 1. Install Dependencies

```bash
pip install gdal fiona shapely pyproj
```

Or use OSGeo4W (Windows):
```powershell
# Download from https://trac.osgeo.org/osgeo4w/
# Install GDAL, GDAL Python bindings, and QGIS (optional)
```

### 2. Download a NOAA ENC

1. Visit https://www.charts.noaa.gov/ENCs/ENCs.shtml
2. Select a region (e.g., "Atlantic Coast - US")
3. Download a chart file (e.g., `US5VA18M.000` for Virginia coastal area)
4. Place in `bridge_sim/areas/noaa_charts/` folder

### 3. Extract Chart Data (Optional)

You can pre-extract the chart to GeoJSON or Shapefile for faster loading:

```bash
# Convert S-57 to GeoJSON
ogr2ogr -f GeoJSON output.geojson input.000

# Or use the Python loader module (see below)
```

## Python Module: `noaa_enc_loader.py`

Located at `tools/noaa_enc_loader.py`, this module provides:

- `ENCAChart` class to load and parse S-57/S-101 files
- Extract layers: coastline, depths, buoys, lights, etc.
- Render as vector geometries in Pygame
- Export to GeoJSON/Shapefile

### Example Usage

```python
from tools.noaa_enc_loader import ENChart

# Load a NOAA ENC file
chart = ENChart('bridge_sim/areas/noaa_charts/US5VA18M.000')

# Get the bounding box (latN, latS, lonW, lonE)
bbox = chart.get_bounds()
print(f"Chart bounds: {bbox}")

# Extract a specific layer (e.g., coastline)
coastline = chart.get_layer('LNDSRF')  # Land surfaces
for geom in coastline:
    print(geom)  # Shapely geometry object

# Export to GeoJSON
chart.export_to_geojson('output.geojson', layers=['LNDSRF', 'DEPCNT', 'BOYINF'])

# Export to Shapefile
chart.export_to_shapefile('output_shp/', layers=['LNDSRF', 'DEPCNT'])

# Get feature data with attributes
features = chart.get_features_with_attributes(layer='LNDSRF')
for feat in features:
    print(feat['properties'])  # NOAA-specific metadata
```

## Integration with ECDIS Display

### Step 1: Modify `bridge_sim/ecdis.py`

Add a method to load NOAA ENC vector layers:

```python
from tools.noaa_enc_loader import ENChart

class ECDISDisplay:
    def load_noaa_enc(self, enc_path):
        """Load and render a NOAA ENC chart as vector layers."""
        self.enc_chart = ENChart(enc_path)
        bbox = self.enc_chart.get_bounds()
        self.latN, self.latS, self.lonW, self.lonE = bbox
        self.vector_layers = {}
        
        # Extract key layers for navigation
        for layer_name in ['LNDSRF', 'DEPCNT', 'BOYINF', 'LIGHTS']:
            try:
                self.vector_layers[layer_name] = self.enc_chart.get_layer(layer_name)
            except:
                pass
    
    def draw_vector_layers(self, ship):
        """Render ENC vector layers on the ECDIS display."""
        for layer_name, geometries in self.vector_layers.items():
            color = self._get_layer_color(layer_name)
            for geom in geometries:
                self._draw_geometry(geom, color)
    
    def _get_layer_color(self, layer_name):
        """Map layer names to display colors."""
        colors = {
            'LNDSRF': (60, 100, 40),    # Green for land
            'DEPCNT': (100, 150, 200),  # Light blue for depth contours
            'BOYINF': (255, 100, 0),    # Orange for buoys
            'LIGHTS': (255, 255, 0),    # Yellow for lights
        }
        return colors.get(layer_name, (100, 100, 100))
    
    def _draw_geometry(self, geom, color):
        """Draw a Shapely geometry on the display."""
        if geom.geom_type == 'LineString':
            pts = [self.ll_to_xy(lat, lon) for lon, lat in geom.coords]
            if len(pts) > 1:
                pg.draw.lines(self.screen, color, False, pts, 1)
        elif geom.geom_type == 'Polygon':
            pts = [self.ll_to_xy(lat, lon) for lon, lat in geom.exterior.coords]
            if len(pts) > 2:
                pg.draw.polygon(self.screen, color, pts)
        elif geom.geom_type == 'Point':
            x, y = self.ll_to_xy(geom.y, geom.x)
            pg.draw.circle(self.screen, color, (int(x), int(y)), 3)
```

### Step 2: Update `main.py` State Handling

```python
def _cycle_state(self):
    # ... existing code ...
    if self.state == 'menu' and self.radar is None:
        ship = Ship(...)
        self.radar = RadarDisplay(...)
        self.ecdis = ECDISDisplay(...)
        
        # Try to load NOAA ENC if available
        enc_path = 'bridge_sim/areas/noaa_charts/US5VA18M.000'
        if os.path.exists(enc_path):
            self.ecdis.load_noaa_enc(enc_path)
```

## Key NOAA ENC Layers

| Layer Code | Name | Description |
|-----------|------|-------------|
| LNDSRF | Land Surface | Coastlines and land areas |
| DEPCNT | Depth Contours | Bathymetry depth lines |
| SOUNDG | Soundings | Point depth measurements |
| BOYINF | Buoy Information | Navigation buoys |
| LIGHTS | Lights | Navigation lights |
| WRECK | Wrecks | Wreck hazards |
| OBSTRN | Obstructions | Underwater obstructions |

## Troubleshooting

### Issue: `gdal` module not found

**Solution:**
```bash
# Windows: Use OSGeo4W installer
# Linux: sudo apt-get install gdal-bin python3-gdal
# macOS: brew install gdal
```

### Issue: S-57 file won't open

**Solution:** Download an unencrypted S-57 file. Encrypted charts require a decryption key.

### Issue: Performance lag with large charts

**Solution:** 
- Pre-extract layers to GeoJSON for faster loading
- Render only visible features (clip to view bounds)
- Cache rendered vector paths

## Next Steps

1. Download a test NOAA ENC file from https://www.charts.noaa.gov/ENCs/ENCs.shtml
2. Run `tools/noaa_enc_loader.py` to test loading and export
3. Integrate the loader into `bridge_sim/ecdis.py`
4. Test rendering in the ECDIS display with ship overlay

---

For more info: https://www.iho.int/iho-registers/page-documents-s-57-s-101
