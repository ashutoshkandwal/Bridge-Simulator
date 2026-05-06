# 🗺️ ECDIS Chart Integration - Complete Setup

## 📦 Your Chart Archive

```
bridge_sim_configurable/
└── bridge_sim/
    └── areas/
        └── Gibraltar Strait.cab (459 MB)
            ├── Area Spec/Gibraltar Strait/Images/
            │   ├── Gibraltar.jpg       ← MAIN CHART
            │   ├── All.jpg
            │   ├── Tanger.jpg
            │   ├── TangerMed.jpg
            │   ├── Tarifa.jpg
            │   └── WtCr.jpg
            ├── 3D Models/
            ├── Checklists/
            └── ... (224 total files)
```

## ⚡ Quick Setup (2 Minutes)

### Step 1: Extract Chart
```bash
cd bridge_sim_configurable
python extract_chart.py
```

### Step 2: Restart Simulator
```bash
python -m bridge_sim.main
```

### Step 3: Enter Position & View Chart
1. Menu appears → Enter lat/lon/heading/speed
2. Press SPACE to start
3. Press SPACE to go to Radar
4. Press SPACE to go to **ECDIS** ← Your chart appears here!

---

## 🎯 Three Ways to Get Your Chart

### Method 1: Automatic Extraction (EASIEST)
```bash
# One command to extract and organize
python extract_chart.py
```
✅ Fastest  
✅ Handles all details  
✅ Recommended  

### Method 2: Manual Windows Extraction
```powershell
cd bridge_sim\areas
expand "Gibraltar Strait.cab" -F:* .
# Then copy: Area Spec\Gibraltar Strait\Images\Gibraltar.jpg → .
```
✅ Simple  
✅ No Python needed  

### Method 3: Generate Sample Chart
```bash
pip install Pillow
python create_sample_chart.py
```
✅ Instant test  
✅ No extraction needed  

---

## 📊 Integration Flow

```
┌─────────────────────────────────────────┐
│  Your CAB Archive in areas/ folder      │
│  Gibraltar Strait.cab (459 MB)          │
└──────────┬──────────────────────────────┘
           │
           ├─→ [Extract with extract_chart.py]
           │
           └─→ Creates: gibraltar.jpg in areas/
                        (or other JPG/PNG images)
                        │
                        ├─→ ECDIS auto-discovers
                        │   on next restart
                        │
                        └─→ Chart displays in
                            ECDIS screen with
                            ship position overlay!
```

---

## 🔄 ECDIS Display Integration

### Chart Search (in order):
1. `bridge_sim/areas/gibraltar.jpg` ← Your extracted chart
2. `bridge_sim/areas/*.jpg` (anything with "gibr" in name)
3. `bridge_sim/areas/*.png` (same)
4. Fallback: schematic coastline

### Auto-Positioning:
- Chart centers on **your ship's GPS position** from menu
- Automatically zooms to ±0.4° around ship
- Lat/Lon grid overlaid for reference
- Ship marked with yellow circle + heading indicator

### Live Features:
- Press `R` in ECDIS to reload chart
- Chart auto-scales to window (900×598)
- Works with PNG, JPG, BMP, GIF formats
- Status shown at bottom: "Loaded: [filename]"

---

## 📁 File Organization After Extraction

### Ideal Setup:
```
bridge_sim_configurable/
├── extract_chart.py           ← Use this first!
├── create_sample_chart.py
├── AREAS_GUIDE.md             ← Full documentation
├── CHART_INTEGRATION.md       ← This guide
└── bridge_sim/
    └── areas/
        ├── Gibraltar Strait.cab    (original archive)
        ├── gibraltar.jpg           ✅ (extracted - ECDIS uses this!)
        ├── all.jpg                 (also available)
        ├── Area Spec/              (extracted folder structure)
        └── Source/                 (3D models, etc.)
```

---

## ✅ Verification Checklist

After extraction, check:

- [ ] File exists: `bridge_sim/areas/gibraltar.jpg`
- [ ] File size > 100 KB (it's a full chart image)
- [ ] ECDIS status says "Loaded: gibraltar.jpg"
- [ ] Yellow ship marker appears on chart
- [ ] Grid overlay visible
- [ ] Lat/Lon coordinates match your entry

**If any fail:** Run `python extract_chart.py` again or see AREAS_GUIDE.md

---

## 🚨 Troubleshooting

### Chart Not Appearing?

**Check 1:** Is JPG in right place?
```powershell
ls bridge_sim/areas/*.jpg
```
Should show `gibraltar.jpg`

**Check 2:** Restart simulator
```bash
python -m bridge_sim.main
```
Chart loads on startup only

**Check 3:** Check ECDIS status
- Go to ECDIS screen
- Read message at bottom
- Will say where it looked or if found

**Check 4:** Manual placement
1. Find `Gibraltar.jpg` anywhere in extracted files
2. Copy to `bridge_sim/areas/`
3. Rename to `gibraltar.jpg` (lowercase)
4. Restart simulator

### Chart Looks Blurry?
- Try higher-resolution source image
- All.jpg might be better than Gibraltar.jpg
- Convert to PNG for best quality

### Want Different Chart Coverage?
1. Edit menu default positions in `main.py`
2. Change `ship_lat`, `ship_lon` to match your chart
3. ECDIS will auto-center on new position

---

## 📚 Additional Resources

| File | Purpose |
|------|---------|
| `AREAS_GUIDE.md` | Detailed extraction methods & troubleshooting |
| `CHART_INTEGRATION.md` | Technical overview |
| `extract_chart.py` | Automated extraction tool |
| `create_sample_chart.py` | Generate test chart |
| `ecdis.py` | ECDIS display code (updated) |

---

## 🎓 Understanding the CAB File

Your `Gibraltar Strait.cab` is a **complete training scenario** containing:

- **Images** (JPG): High-resolution nautical charts
- **3D Models** (ITF): Port infrastructure, buildings, cranes
- **Scenario** (SCT): Training scenario configuration
- **Checklists** (HTML): 5 training checklists
- **Prototypes** (ITF/ODF): 200+ reusable 3D objects

For ECDIS, we just need the **images** (JPG files).

---

## 🎯 Final Steps

### NOW:
1. Run: `python extract_chart.py`
2. Wait for extraction
3. Verify: `gibraltar.jpg` appears in `bridge_sim/areas/`

### THEN:
1. Run simulator: `python -m bridge_sim.main`
2. Enter your position & heading
3. Navigate to ECDIS (SPACE, SPACE from menu)
4. **See your chart with ship overlay!** 🚢

---

**Ready?** Start with: `python extract_chart.py`
