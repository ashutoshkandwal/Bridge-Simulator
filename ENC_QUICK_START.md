# NOAA ENC Quick Start

## ✅ Status

Your system has:
- GDAL 3.10.3 ✓
- Fiona ✓
- Shapely ✓
- ECDIS ENC integration ✓

## 📥 Get a Chart

```powershell
# 1. Download from https://www.charts.noaa.gov/ENCs/ENCs.shtml
# 2. Place in bridge_sim/areas/noaa_charts/
# 3. Example: US5VA18M.000 (~15 MB)

mkdir "bridge_sim\areas\noaa_charts"
```

## 🧪 Test the Loader

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

Output: Layers loaded, bounds printed, `chart_export.geojson` created ✓

## 🖼️ Render in Simulator

### Option A: Quick Standalone Test

Create `test_run_with_enc.py` (example in full guide):

```powershell
python test_run_with_enc.py
```

### Option B: Integrate into Main

In `bridge_sim/main.py`, after creating `ECDISDisplay`:

```python
ecdis.load_noaa_enc("bridge_sim/areas/noaa_charts/US5VA18M.000")
```

Then run the main simulator normally.

## 📋 What Gets Rendered

- **LNDSRF** – Land (brown)
- **DEPCNT** – Depth contours (light blue)
- **COALNE** – Coastline (dark blue)
- **BUOYS** – Buoys (yellow)
- **LIGHTS** – Light structures (bright yellow)

Colors customizable in `bridge_sim/ecdis.py` → `draw_enc_layers()` → `layer_colors` dict.

## 📖 Full Details

See **ENC_INTEGRATION_GUIDE.md** for:
- Layer descriptions
- Performance tuning
- Troubleshooting
- API reference

---

**In gdal_env?** Check: `python test_enc_simple.py` should show ✓ for all dependencies.
