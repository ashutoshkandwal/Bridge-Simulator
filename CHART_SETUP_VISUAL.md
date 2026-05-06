# ECDIS Chart Setup - Visual Guide

## 🎯 Your Goal
Get the **Gibraltar Strait chart from your CAB file** displaying in the ECDIS screen.

---

## 📊 Current State vs End State

### BEFORE (Now):
```
Simulator starts
       ↓
Menu → Enter position/heading/speed
       ↓
Radar Screen → Works perfectly ✓
       ↓
ECDIS Screen → Shows schematic coastline only
               (because no chart image found)
```

### AFTER (Goal):
```
Simulator starts
       ↓
Menu → Enter position/heading/speed
       ↓
Radar Screen → Works perfectly ✓
       ↓
ECDIS Screen → Shows YOUR extracted chart! 🗺️
               Ship marker overlay ✓
               Lat/Lon grid ✓
               Status: "Loaded: gibraltar.jpg"
```

---

## 🔧 Setup Pipeline

```
┌──────────────────────────────────────┐
│  Gibraltar Strait.cab                │
│  (in bridge_sim/areas/)              │
│  459 MB archive file                 │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
AUTOMATIC            MANUAL
extract_chart.py    Right-click extract
    │                     │
    └──────────┬──────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Extracted folder:   │
    │  Area Spec/          │
    │  Gibraltar Strait/   │
    │  Images/             │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  JPG files:          │
    │  • Gibraltar.jpg     │
    │  • All.jpg           │
    │  • Tanger.jpg        │
    │  • TangerMed.jpg     │
    │  • Tarifa.jpg        │
    │  • WtCr.jpg          │
    └──────────┬───────────┘
               │ (Copy one to:)
               │ bridge_sim/areas/
               ▼
    ┌──────────────────────┐
    │  gibraltar.jpg       │
    │  (in areas folder)   │
    └──────────┬───────────┘
               │
    (Simulator restarts)
               │
               ▼
    ┌──────────────────────┐
    │  ECDIS auto-finds    │
    │  & loads chart!      │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Chart displays in   │
    │  ECDIS with:         │
    │  ✓ Ship overlay      │
    │  ✓ Grid lines        │
    │  ✓ Coordinates       │
    └──────────────────────┘
```

---

## ⏱️ Time Estimate

| Step | Time | Action |
|------|------|--------|
| 1 | <1 min | Run extraction script |
| 2 | 1-2 min | Extraction completes |
| 3 | <1 min | Copy chart file |
| 4 | <1 min | Restart simulator |
| 5 | <1 min | Enter your position |
| 6 | <1 min | Navigate to ECDIS |
| **TOTAL** | **~5 min** | **Chart visible!** |

---

## 🚀 Quick Reference Commands

```bash
# Extract your chart
python extract_chart.py

# Generate test chart (if extract fails)
pip install Pillow
python create_sample_chart.py

# Run simulator
python -m bridge_sim.main
```

---

## 📍 Chart Auto-Centering Explained

### Your Input (Menu):
```
Latitude:  36.15°N
Longitude: 5.50°W
```

### ECDIS Does This:
```
1. Reads your coordinates
2. Sets chart bounds:
   North: 36.15 + 0.4 = 36.55°N
   South: 36.15 - 0.4 = 35.75°N
   West:  5.50 - 0.4 = 5.90°W
   East:  5.50 + 0.4 = 5.10°W

3. Maps your position to:
   Center of 900×598 pixel display

4. Overlays:
   • Yellow circle (ship)
   • Heading line (direction)
   • Lat/Lon grid (0.05° intervals)
```

### Result:
Chart shows your ship in center with ~50 km radius view

---

## 🎨 What You'll See in ECDIS

```
┌─────────────────────────────────────────┐
│  Chart Training Aid — Strait of         │
│  Gibraltar                              │
│                                         │
│    Land    ▲ ▲ ▲ ▲ ▲   Spain           │
│  ▲▲▲▲▲▲▲  ▲ ▲ ▲ ▲ ▲   (North)        │
│ ▲▲ Grid  ▲ ▲ ▲ ▲ ▲ ▲                  │
│ ▲   ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲                │
│ ▲ ▲ ▲ ▲  ★ ← Your Ship (Yellow)       │
│ ▲   ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲                  │
│ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲                  │
│  ▲▲▲▲▲▲▲  ▲ ▲ ▲ ▲ ▲                   │
│    Land    ▲ ▲ ▲ ▲ ▲                   │
│           Morocco                      │
│           (South)                      │
├─────────────────────────────────────────┤
│ Loaded: gibraltar.jpg    R to reload    │
└─────────────────────────────────────────┘
```

- **Grid lines**: Lat/Lon coordinates
- **★ (Yellow circle)**: Your ship position
- **| line**: Your heading direction
- **Land areas**: Darker (scaled from image)
- **Water**: Blue background
- **Status bar**: Shows which chart is loaded

---

## 🔄 During Simulation

### Keyboard Controls in ECDIS:
- **SPACE** - Cycle to next screen (Controls → Menu)
- **R** - Reload chart from disk
- **Arrow keys** - (Not implemented yet, but could zoom/pan)

### What Updates:
- Ship position moves as time passes
- Heading line rotates with ship
- Grid stays fixed

### What's Static:
- Chart image (doesn't scroll, but could be added)
- Coast lines and features

---

## 💾 File Size Reference

| Item | Size |
|------|------|
| Gibraltar Strait.cab (compressed) | 459 MB |
| Gibraltar.jpg (extracted) | ~3-5 MB |
| All.jpg (extracted) | ~5-8 MB |
| Sample generated chart (PNG) | ~50-100 KB |

---

## ✨ Features Enabled After Setup

### Chart Display:
- ✅ Automatic chart loading
- ✅ Chart centering on ship position
- ✅ Lat/Lon grid overlay
- ✅ Ship position marking
- ✅ Heading direction line
- ✅ Live reload (press R)

### Not Yet Implemented (future):
- ⏳ Chart panning/scrolling
- ⏳ Zoom in/out
- ⏳ Multiple chart layers
- ⏳ Target plotting
- ⏳ Route display

---

## 🎓 Understanding Each Component

### The CAB Archive (459 MB):
- Container format from professional shipping simulator
- Contains complete training scenario
- We only need the image files inside

### Chart Images (JPG):
- High-resolution nautical charts
- Georeferenced to lat/lon coordinates
- Multiple views of Gibraltar Strait area
- **Gibraltar.jpg** = main chart (recommended)

### ECDIS Integration:
- Automatically discovers chart images
- Scales to display window (900×598)
- Maps geographic coordinates to pixel positions
- Centers on your ship's starting position

### Auto-Positioning System:
- Reads your menu input (lat/lon/heading/speed)
- Sets appropriate chart bounds
- Renders ship marker at calculated position
- Updates heading indicator

---

## ✅ Success Indicators

After setup, you should see:

1. **Extraction runs without errors**
   ```
   ✓ Extracting: Gibraltar Strait.cab
   ✓ Found 6 chart images
   ✓ Copied to: bridge_sim/areas/
   ```

2. **File appears in folder**
   ```
   bridge_sim/areas/gibraltar.jpg (exists, 4.2 MB)
   ```

3. **Simulator loads chart**
   ```
   ECDIS Status: "Loaded: gibraltar.jpg"
   ```

4. **Chart displays with overlay**
   ```
   - Chart image visible (pixelated/gridded)
   - Yellow circle (ship) visible in center
   - Heading line visible
   - Lat/Lon grid visible
   ```

---

## 🆘 Something Not Working?

### Quick Fixes:
1. **File not found?** → Run `python extract_chart.py` again
2. **Blurry chart?** → Use All.jpg instead of Gibraltar.jpg
3. **Wrong position?** → Check menu input was saved
4. **Need sample?** → Run `python create_sample_chart.py`

See **AREAS_GUIDE.md** for complete troubleshooting!

---

**Ready to proceed?** Run: `python extract_chart.py`
