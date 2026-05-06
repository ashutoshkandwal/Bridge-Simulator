# Areas Folder - Chart Integration Guide

## Overview
The `bridge_sim/areas/` folder contains nautical chart data for your ECDIS (Electronic Chart Display Information System) display.

## Current Contents
- **Gibraltar Strait.cab** (459 MB) - CAB archive containing detailed Gibraltar Strait chart data
  - Contains multiple image files (JPG format)
  - Contains 3D model objects (ITF format)
  - Contains configuration and checklist files

## How to Use Your Chart in ECDIS

### Option 1: Extract Images from the CAB File (Recommended)

The `Gibraltar Strait.cab` contains chart images. To use them:

#### Windows Extract (Recommended)
```powershell
cd bridge_sim\areas
expand "Gibraltar Strait.cab" -F:* .
```

This will extract files including:
- `Area Spec\Gibraltar Strait\Images\Gibraltar.jpg`
- `Area Spec\Gibraltar Strait\Images\All.jpg`
- `Area Spec\Gibraltar Strait\Images\Tanger.jpg`

**Note:** You may get error `0xca00a009` - this is normal for partial CAB files. The JPG images should extract successfully.

#### Manual Extraction
1. Right-click `Gibraltar Strait.cab`
2. Select "Extract All..."
3. Choose destination folder
4. Navigate to `Area Spec\Gibraltar Strait\Images\`
5. Copy the JPG files to `bridge_sim/areas/`

### Option 2: Use Auto-Generated Chart (Quick Test)

If you want to test immediately without extracting:

```bash
cd bridge_sim_configurable
python create_sample_chart.py
```

This generates a simple procedurally-created chart image.

**Requires:** `pip install Pillow`

### Option 3: Convert CAB to Image Files Using Python

```python
# Extract specific JPG from CAB and place in areas folder
import zipfile
import shutil

cab_path = "bridge_sim/areas/Gibraltar Strait.cab"

# CAB files can sometimes be treated as ZIP
try:
    with zipfile.ZipFile(cab_path, 'r') as zip_ref:
        jpg_files = [f for f in zip_ref.namelist() if f.lower().endswith('.jpg')]
        for jpg in jpg_files:
            zip_ref.extract(jpg, "bridge_sim/areas/")
            print(f"Extracted: {jpg}")
except Exception as e:
    print(f"Could not extract as ZIP: {e}")
```

## Chart Image Naming Convention

The ECDIS looks for images with these names (in order of priority):
1. `gibraltar.png`
2. `chart_gibraltar.png`
3. `strait_of_gibraltar.png`
4. `strait_gibraltar.png`
5. Any PNG/JPG with "gibr" in the filename in `bridge_sim/` or `bridge_sim/areas/` folders

## Supported Image Formats
- PNG (lossless)
- JPG/JPEG (lossy, faster loading)
- BMP
- GIF

## Chart Display in ECDIS

Once you have a chart image:

1. **Automatic Loading:**
   - Restart the simulator
   - Navigate to ECDIS screen (press SPACE twice from menu)
   - Chart should load automatically if found

2. **Reload During Runtime:**
   - Press `R` while viewing ECDIS to reload the chart

3. **Status Display:**
   - Chart status shown at bottom of ECDIS screen
   - Will display "Loaded: [filename]" or "No chart image found"

## Chart Mapping

The chart is automatically mapped to geographic coordinates:
- **Center:** Your ship's starting position (from menu)
- **View:** ±0.4° around ship position
- **Grid:** Lat/Lon grid overlaid (0.05° intervals)

### Chart Bounds (default for Gibraltar)
- **North:** 36.55°N
- **South:** 35.75°N  
- **West:** 5.90°W
- **East:** 4.90°W

These are automatically centered on your ship's position.

## Troubleshooting

### Chart Not Loading?
1. Check that image file is in `bridge_sim/areas/` folder
2. Verify filename contains "gibraltar" or matches naming convention
3. Try JPG format instead of PNG
4. Check ECDIS status message for error details

### Chart Appears Blurry?
- Images are automatically scaled to 900x598 pixels
- Use high-resolution source images for better quality

### Want Different Chart Areas?
1. Extract different images from the CAB file
2. Rename to `gibraltar.png`
3. Adjust `ship_lat`, `ship_lon` in menu to match your chart bounds
4. ECDIS will automatically re-center

## CAB File Contents Summary

The `Gibraltar Strait.cab` contains:
- **Images:** Multiple chart photographs (JPG)
- **3D Models:** Port infrastructure (ITF format)
- **Checklists:** 5 training checklists (HTML)
- **Scenario:** Main scenario file (SCT format)
- **3D Prototypes:** Extensive object library for 3D scene building

Total: 224 files including detailed port infrastructure and navigation aids.

## Next Steps

1. Extract chart images from CAB file (or generate sample)
2. Place chart image as `gibraltar.png` in `bridge_sim/areas/`
3. Restart simulator
4. Enter your ship position and navigate to ECDIS screen
5. Your custom chart should display!

---

**Need Help?**
- For CAB extraction issues: Use Windows File Explorer right-click extract
- For image format issues: Convert to PNG using any image editor
- For chart positioning: Adjust ship coordinates in menu to match your chart area
