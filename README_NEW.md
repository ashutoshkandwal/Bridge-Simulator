# Bridge Simulator — Configurable Radar & ECDIS with NOAA ENC

Professional bridge navigation simulator with Pygame, featuring configurable radar (PPI) display and professional NOAA electronic navigational charts.

## 🚀 Quick Start

### Basic Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run simulator
python bridge_sim/main.py
```

### With NOAA ENC Charts (Professional Vector Navigation)
```bash
# 1. Set up GDAL environment
conda activate gdal_env

# 2. Download a test chart from https://www.charts.noaa.gov/ENCs/ENCs.shtml
mkdir bridge_sim/areas/noaa_charts
# Place chart.000 file in this folder

# 3. Run with ENC support
python bridge_sim/main.py
# Navigate to ECDIS mode to see professional vector charts
```

**For detailed setup:** See **NEXT_STEPS.md** (copy/paste commands)

---

## ✨ Features

### Radar Display (PPI — Plan Position Indicator)
- 360° sweep with configurable range rings
- Real-time ship position and heading vector
- Menu-based configuration (no code editing)

### Chart Display (ECDIS — Electronic Chart Display & Information System)
- **PNG Raster Charts** with JSON georeference metadata
- **NOAA S-57/S-101 Vector Charts (ENC)** — Professional nautical data
  - Coastlines, depth contours, buoys, navigational lights
  - Color-coded by feature type
  - Renders from standard NOAA format
- Static chart with dynamic ship overlay
- Geographic grid with lat/lon labels

### Ship Navigation
- Heading + speed control
- Real-time position updates
- Configurable start position via menu

### Configuration
Edit **config.json** for:
- Range ring steps (nautical miles)
- Display colors and themes
- UI button/panel positions
- Chart selection

---

## 📊 NOAA ENC Support

### What is ENC?
Electronic Navigational Charts — official NOAA charts in S-57/S-101 format.
- Professional-grade vector data
- Regularly updated by NOAA
- Free public access

### Supported Chart Types
| Format | File Extension | Description |
|--------|---|---|
| S-57 | `.000`, `.001`, etc. | Standard ENC format (most common) |
| S-101 | `.gpkg` | New GeoPackage format |

### Available Features
| Layer | Description | Visual Color |
|-------|---|---|
| **LNDSRF** | Land surfaces | Brown (100, 100, 80) |
| **DEPCNT** | Depth contours | Light blue (150, 150, 200) |
| **COALNE** | Coastline | Dark blue (80, 120, 150) |
| **SLCONS** | Shoreline complex | Medium blue (100, 150, 180) |
| **BUOYS** | Navigation buoys | Yellow (255, 200, 0) |
| **LIGHTS** | Light structures | Bright yellow (255, 255, 100) |

### Download Charts
Visit: **https://www.charts.noaa.gov/ENCs/ENCs.shtml**

Popular test regions:
- **US5VA18M** — Chesapeake Bay (good starting point, ~15 MB)
- **US4MD12M** — Mid-Atlantic coast
- Any region with appropriate coverage

---

## 📁 Project Structure

```
bridge_sim_configurable/
├── bridge_sim/                    # Main simulator package
│   ├── main.py                    # Entry point + event loop
│   ├── models.py                  # Ship class
│   ├── ecdis.py                   # Chart display (PNG + ENC)
│   ├── radar.py                   # PPI radar display
│   ├── controls.py                # Control panel UI
│   ├── ui.py                      # UI utilities
│   └── areas/                     # Charts storage
│       ├── chart_gibraltar.png    # Sample raster chart
│       ├── chart_gibraltar.json   # Georeference metadata
│       └── noaa_charts/           # ENC files (user-provided)
│           └── US5VA18M.000       # Example: Chesapeake Bay S-57
│
├── tools/                         # Utility scripts
│   ├── noaa_enc_loader.py         # ENChart class for ENC loading
│   └── convert_chart_to_geotiff.py # Raster utilities
│
├── tests/                         # Test scripts
│   ├── test_enc_simple.py         # Dependency verification
│   └── test_enc_integration.py    # Full integration test
│
├── config.json                    # Configuration (no code editing needed)
├── requirements.txt               # Pip dependencies
│
├── README.md                      # This file
├── NEXT_STEPS.md                  # Copy/paste setup commands
├── ENC_QUICK_START.md             # One-page ENC reference
├── ENC_INTEGRATION_GUIDE.md       # Comprehensive ENC guide
├── SETUP_COMPLETE.md              # Installation summary
└── ARCHITECTURE.txt               # System design overview
```

---

## ⚙️ Configuration (config.json)

Customize without editing Python code:

```json
{
  "ranges_nm": [0.5, 1, 2, 4, 8, 16, 32],
  "ppi_radius_px": 150,
  "colors": {
    "water": [5, 30, 40],
    "land": [60, 60, 60],
    "grid": [40, 120, 180],
    "ship_marker": [255, 255, 0]
  },
  "ui_positions": {
    "right_panel": [920, 10, 350, 600],
    "buttons": {
      "range_up": [940, 100, 60, 30],
      "range_dn": [1010, 100, 60, 30]
    }
  }
}
```

**Key settings:**
- `ranges_nm` — Range ring steps. Add/remove freely (e.g., `[0.5, 1, 2, 4, 8]`)
- `colors` — RGB tuples. Change theme by editing values
- `ui_positions` — Move buttons/panels by changing `[x, y, width, height]`

---

## 🧪 Verification & Testing

### 1. Check Installation
```bash
python test_enc_simple.py
```

Expected output:
```
✓ GDAL 3.10.3 available
✓ Fiona available
✓ Shapely available
✓ ENC loader module available
```

### 2. Test Chart Loading
```bash
python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

Expected: Layers printed, bounds shown, `chart_export.geojson` created.

### 3. Test Simulator with ENC
```bash
python bridge_sim/main.py
# Menu → enter coords → select ECDIS
# Should render ENC chart with ship marker
```

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: pygame"
```bash
pip install pygame
```

### "ModuleNotFoundError: osgeo" (GDAL)
```bash
# Activate GDAL environment
conda activate gdal_env
python bridge_sim/main.py
```

### ENC chart not rendering
1. Verify setup: `python test_enc_simple.py` (all should show ✓)
2. Check file path: `Test-Path "bridge_sim/areas/noaa_charts/chart.000"` (should be True)
3. Check console for `[ENC] Opened:` message
4. See **ENC_INTEGRATION_GUIDE.md** for detailed troubleshooting

### Chart position wrong
Edit `bridge_sim/areas/chart_gibraltar.json` georeference:
```json
{
  "latN": 36.217,
  "latS": 35.667,
  "lonW": -6.333,
  "lonE": -5.25
}
```

---

## 🛠️ Development

### Adding a New PNG Chart
1. Place image in `bridge_sim/areas/`
2. Create JSON sidecar with same name:
   ```json
   {
     "latN": 36.5,
     "latS": 35.5,
     "lonW": -6.5,
     "lonE": -5.0
   }
   ```
3. Restart; chart auto-loads

### Adding an ENC Chart
1. Download S-57 file from NOAA
2. Place in `bridge_sim/areas/noaa_charts/`
3. In `bridge_sim/main.py`, after `ECDISDisplay` creation:
   ```python
   ecdis.load_noaa_enc("bridge_sim/areas/noaa_charts/YOUR_CHART.000")
   ```
4. Restart; ENC layers auto-render

### Customizing ENC Colors
Edit `bridge_sim/ecdis.py`, find `draw_enc_layers()` method:
```python
layer_colors = {
    'LNDSRF': (100, 100, 80),    # Change RGB values
    'DEPCNT': (150, 150, 200),   # 0-255 per channel
    # ... etc
}
```

---

## 📚 Documentation

| File | Contents |
|------|---|
| **README.md** | This file — overview & quick start |
| **NEXT_STEPS.md** | Copy/paste commands for setup & testing |
| **ENC_QUICK_START.md** | One-page ENC reference |
| **ENC_INTEGRATION_GUIDE.md** | Comprehensive ENC guide + API docs |
| **SETUP_COMPLETE.md** | Installation summary |
| **ARCHITECTURE.txt** | System design & data flow diagram |

---

## 🔐 Requirements

### Core
- **Python** 3.10+
- **Pygame** 2.0+ (graphics)

### For NOAA ENC Support (Optional)
- **GDAL** 3.0+ (geospatial data I/O)
- **Fiona** (OGR wrapper)
- **Shapely** (geometry operations)
- **PyProj** (coordinate transformations)

All listed in `requirements.txt` for pip. For Conda + GDAL setup, see **NEXT_STEPS.md**.

---

## 🎯 Usage Workflow

### Scenario: Test with NOAA Chart

1. **Setup**
   ```bash
   conda activate gdal_env
   python test_enc_simple.py          # Verify all dependencies
   ```

2. **Get Chart**
   - Download from https://www.charts.noaa.gov/ENCs/ENCs.shtml
   - Place in `bridge_sim/areas/noaa_charts/`

3. **Run Simulator**
   ```bash
   python bridge_sim/main.py
   ```

4. **In Simulator**
   - Enter ship coordinates matching chart region
   - Select **ECDIS** mode
   - See professional chart render with ship marker

---

## 📝 Example: Custom Integration

Create `my_custom_test.py`:

```python
import pygame as pg
from bridge_sim.models import Ship
from bridge_sim.ecdis import ECDISDisplay

pg.init()
screen = pg.display.set_mode((1280, 800))

# Create ship at Chesapeake Bay (for US5VA18M)
ship = Ship(lat=37.0, lon=-76.0, heading=90, speed=10)

# Create ECDIS
ecdis = ECDISDisplay(screen, ship=ship, follow_ship=False)

# Load ENC
ecdis.load_noaa_enc("bridge_sim/areas/noaa_charts/US5VA18M.000")

# Render
clock = pg.time.Clock()
while True:
    dt = clock.tick(60) / 1000.0
    ship.update_position(dt, north=0)
    screen.fill((0, 0, 0))
    ecdis.draw(ship)
    pg.display.flip()

pg.quit()
```

Run: `python my_custom_test.py`

---

## 🌐 Resources

- **NOAA Charts** — https://www.charts.noaa.gov/ENCs/ENCs.shtml
- **GDAL/OGR** — https://gdal.org/
- **Pygame** — https://www.pygame.org/
- **Shapely** — https://shapely.readthedocs.io/

---

## 📄 License & Attribution

Educational bridge navigation simulator.

Uses:
- **Pygame** — 2D graphics library
- **GDAL/OGR** — Geospatial data libraries
- **NOAA ENC Charts** — Public nautical data (free, public domain)

---

## 🚀 Get Started

```bash
# 1. Install basic dependencies
pip install -r requirements.txt

# 2. Run simulator
python bridge_sim/main.py

# 3. For NOAA charts, follow NEXT_STEPS.md
```

**Questions?** Refer to documentation files above.

Enjoy your bridge simulator! ⚓
