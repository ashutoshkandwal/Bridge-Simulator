# 📖 Bridge Simulator - Complete Documentation Index

## 🎯 Quick Navigation

### ⚡ I Want To... 

**Get my chart working in ECDIS (5 min)**
→ Read: [`SETUP_CHART.md`](SETUP_CHART.md)
```bash
python extract_chart.py
python -m bridge_sim.main
```

**Understand the chart setup visually**
→ Read: [`CHART_SETUP_VISUAL.md`](CHART_SETUP_VISUAL.md)

**Extract my CAB archive manually**
→ Read: [`AREAS_GUIDE.md`](AREAS_GUIDE.md)

**Troubleshoot chart issues**
→ Read: [`AREAS_GUIDE.md`](AREAS_GUIDE.md#troubleshooting) (Troubleshooting section)

**Understand the technical implementation**
→ Read: [`CHART_INTEGRATION.md`](CHART_INTEGRATION.md)

**See all changes made**
→ Read: [`CHART_SETUP_SUMMARY.md`](CHART_SETUP_SUMMARY.md)

**Learn how the simulator works**
→ Read: [`README.md`](README.md)

**See recent updates**
→ Read: [`CHANGES.md`](CHANGES.md)

---

## 📚 Documentation Files

### Getting Started
| File | Purpose | Read Time |
|------|---------|-----------|
| **SETUP_CHART.md** | Quick 2-step chart setup guide | 2 min |
| **CHART_SETUP_VISUAL.md** | Visual diagrams and flowcharts | 5 min |
| **README.md** | Project overview | 3 min |

### Detailed Guides
| File | Purpose | Read Time |
|------|---------|-----------|
| **AREAS_GUIDE.md** | Complete chart integration guide | 10 min |
| **CHART_INTEGRATION.md** | Technical implementation details | 8 min |
| **CHART_SETUP_SUMMARY.md** | Comprehensive summary of changes | 10 min |

### Reference
| File | Purpose | Read Time |
|------|---------|-----------|
| **CHANGES.md** | Ship setup menu features added | 3 min |
| **This file** | Documentation index | 2 min |

---

## 🛠️ Tools Available

### For Chart Setup
```bash
# Extract chart images from CAB archive (RECOMMENDED)
python extract_chart.py

# Generate test chart (if extraction fails)
pip install Pillow
python create_sample_chart.py
```

### For Running Simulator
```bash
# Install dependencies
pip install -r requirements.txt

# Run simulator
python -m bridge_sim.main
```

---

## 📁 Project Structure

```
bridge_sim_configurable/
│
├── 📖 Documentation Files
│   ├── README.md                    ← Project overview
│   ├── CHANGES.md                   ← Recent features
│   ├── SETUP_CHART.md               ← Quick start (START HERE!)
│   ├── CHART_SETUP_VISUAL.md        ← Visual guide
│   ├── CHART_INTEGRATION.md         ← Technical details
│   ├── CHART_SETUP_SUMMARY.md       ← Summary of changes
│   ├── AREAS_GUIDE.md               ← Complete integration guide
│   └── INDEX.md                     ← This file
│
├── 🔧 Setup Tools
│   ├── extract_chart.py             ← Extract CAB archive
│   └── create_sample_chart.py       ← Generate test chart
│
├── ⚙️ Configuration
│   ├── config.json                  ← UI positioning & colors
│   └── requirements.txt             ← Python dependencies
│
└── 🐍 bridge_sim/ (Main Application)
    ├── main.py                      ← App class & menu
    ├── radar.py                     ← Radar display
    ├── ecdis.py                     ← Electronic chart (UPDATED!)
    ├── models.py                    ← Ship & Target classes
    ├── ui.py                        ← UI widgets
    ├── panel.py                     ← Info panel
    ├── controls.py                  ← Keyboard controls
    ├── utils.py                     ← Utility functions
    └── areas/
        └── Gibraltar Strait.cab     ← Your chart archive (459 MB)
```

---

## 🚀 Getting Started (5 Minutes)

### Step 1: Extract Chart
```bash
# From project root directory
python extract_chart.py
```
Expected output:
```
✓ Extraction complete!
✓ Found 6 chart images
✓ Copied to: bridge_sim/areas/gibraltar.jpg
```

### Step 2: Run Simulator
```bash
python -m bridge_sim.main
```

### Step 3: Enter Your Ship Data
Menu appears with input fields:
- Latitude: **36.15** (°N)
- Longitude: **5.50** (°W)
- Heading: **45** (°T)
- Speed: **24** (kn)

### Step 4: Navigate to ECDIS
- Press **SPACE** → Goes to Radar screen
- Press **SPACE** → Goes to ECDIS screen ← Your chart appears here!

### Step 5: See Your Chart!
Display shows:
- Your extracted Gibraltar chart
- Yellow ship marker in center
- Heading line pointing your direction
- Lat/Lon grid overlay
- Status: "Loaded: gibraltar.jpg"

---

## 📋 Feature Overview

### Menu (New!)
- ✅ Ship position input (Lat/Lon)
- ✅ Heading & speed configuration
- ✅ Input validation
- ✅ Default values provided

### Radar Display
- ✅ PPI (Plan Position Indicator)
- ✅ Configurable ranges (0.75-48 NM)
- ✅ North Up / Course Up modes
- ✅ True Motion / Relative Motion
- ✅ EBL/VRM tools
- ✅ Gain/Sea/Rain controls
- ✅ Real-time heading/speed display

### ECDIS Chart Display (Updated!)
- ✅ Automatic chart loading
- ✅ Multiple image formats (PNG, JPG, BMP, GIF)
- ✅ Auto-centering on ship position
- ✅ Lat/Lon grid overlay
- ✅ Ship position marking
- ✅ Heading indicator
- ✅ Live reload capability (R key)

### Controls
- ✅ Full keyboard mapping
- ✅ Hotkey system
- ✅ Screen cycling

---

## 🎓 Key Concepts

### Ship Setup
The simulator now requires you to input your ship's initial position, heading, and speed. This data:
- **Positions the ship** on the radar at the specified heading/speed
- **Centers the ECDIS chart** on your GPS coordinates
- **Sets the reference frame** for all displays

### Chart Auto-Centering
When you enter a position like 36.15°N, 5.50°W:
1. ECDIS calculates chart bounds (±0.4° margin)
2. Charts scales to cover this geographic area
3. Your ship is marked in the center
4. Grid shows lat/lon coordinates

### Coordinate System
- **Latitude**: North/South (°N / °S)
- **Longitude**: East/West (°W / °E)
- **Heading**: True bearing (°T) from 0-360°
- **Speed**: Knots (kn) / Nautical miles per hour

---

## 🔧 Configuration

### Chart Images
- **Location**: `bridge_sim/areas/`
- **Format**: PNG, JPG, BMP, GIF
- **Naming**: Any name with "gibraltar" in it works
- **Size**: Automatically scaled to 900×598 pixels

### UI Positions & Colors
- **File**: `config.json`
- **Button positions**: Pixel coordinates (x, y, width, height)
- **Colors**: RGB arrays (0-255 per channel)
- **Ranges**: NM steps for radar display

### Keyboard Controls
- **File**: `bridge_sim/controls.py`
- **Hotkeys**: G, S, H, E, V + arrow keys
- **Screen toggle**: SPACE
- **Chart reload**: R (in ECDIS)

---

## 🧪 Testing Your Setup

### Quick Test
```bash
# Extract and run
python extract_chart.py
python -m bridge_sim.main

# Enter default values, press SPACE twice to ECDIS
# Chart should display immediately
```

### Verify Chart Loading
- Check ECDIS status message (bottom of screen)
- Should say: `"Loaded: gibraltar.jpg"`
- If says "No chart image found": See AREAS_GUIDE.md

### Test Different Positions
- Try different lat/lon values in menu
- Chart auto-centers appropriately
- Ship marker stays in center

---

## 📞 Common Tasks

### Extract Chart
**File**: `extract_chart.py`
```bash
python extract_chart.py
```

### Generate Test Chart
**File**: `create_sample_chart.py`
```bash
pip install Pillow
python create_sample_chart.py
```

### Reload Chart During Runtime
**Keyboard**: Press `R` in ECDIS screen

### Check Chart Status
**Display**: Bottom of ECDIS screen shows status

### Change Chart Area
**Method**: Adjust lat/lon in menu, restart simulator

### Use Different Chart Image
**Method**: Place new image in `bridge_sim/areas/` as `gibraltar.jpg`

---

## ❓ Frequently Asked Questions

**Q: Where do I put my chart image?**
A: `bridge_sim/areas/` folder with name like `gibraltar.jpg`

**Q: My chart doesn't show up**
A: See AREAS_GUIDE.md Troubleshooting section

**Q: Can I use a different chart?**
A: Yes! Place any chart image in areas/ folder with "gibraltar" in name

**Q: How do I zoom/pan the chart?**
A: Not yet implemented - change lat/lon in menu to shift view

**Q: Can I plot multiple targets?**
A: Not on chart yet - future enhancement

**Q: What if CAB extraction fails?**
A: Use `python create_sample_chart.py` for a test chart

**Q: Can I use real nautical charts?**
A: Yes, convert to PNG/JPG and place in areas/ folder

**Q: How long to set up?**
A: ~5 minutes total including extraction

---

## 🔗 Related Files

### Source Code
- `bridge_sim/main.py` - Menu implementation
- `bridge_sim/ecdis.py` - Chart loading (UPDATED!)
- `bridge_sim/radar.py` - Radar display
- `bridge_sim/models.py` - Ship class

### Configuration
- `config.json` - UI layout and colors
- `requirements.txt` - Python dependencies

### Tools
- `extract_chart.py` - CAB extraction
- `create_sample_chart.py` - Chart generation

---

## 🎯 Your Current Situation

**What you have:**
- ✅ Bridge simulator with radar display
- ✅ Menu for ship position input
- ✅ ECDIS screen ready for charts
- ✅ 459 MB CAB file with chart images

**What you need to do:**
1. Extract chart images (`python extract_chart.py`)
2. Run simulator (`python -m bridge_sim.main`)
3. Enter position and navigate to ECDIS
4. See your chart! 🗺️

**Time to complete:** ~5 minutes

---

## 📞 Support Resources

- **Setup Issues**: See `SETUP_CHART.md`
- **Chart Extraction**: See `AREAS_GUIDE.md`
- **Technical Details**: See `CHART_INTEGRATION.md`
- **Visual Explanation**: See `CHART_SETUP_VISUAL.md`
- **Troubleshooting**: See `AREAS_GUIDE.md#troubleshooting`

---

## 🎉 Next Steps

1. **Now**: Read `SETUP_CHART.md` (2 min)
2. **Next**: Run `python extract_chart.py` (2 min)
3. **Then**: Run `python -m bridge_sim.main` (1 min)
4. **Finally**: Enter position and see your chart! (1 min)

**Total time: ~5 minutes**

---

**Ready to get started?** → Open [`SETUP_CHART.md`](SETUP_CHART.md)
