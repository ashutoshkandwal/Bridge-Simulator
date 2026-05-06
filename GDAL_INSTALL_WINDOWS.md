# GDAL Installation Guide for Windows

## Overview

GDAL is required to read NOAA ENC charts. On Windows, the easiest method is **OSGeo4W**, which bundles GDAL with Python bindings.

## Step-by-Step Installation

### Step 1: Download OSGeo4W

1. Go to: https://trac.osgeo.org/osgeo4w/
2. Click the large **OSGeo4W installer** button (or use the mirror link if main is slow)
3. Save `osgeo4w-setup.exe` to your Downloads folder
4. You'll see two download links; choose the appropriate one:
   - **32-bit**: `osgeo4w-setup.exe` (if your Python is 32-bit)
   - **64-bit**: `osgeo4w-setup-x86_64.exe` (if your Python is 64-bit — **most likely this one**)

**Check your Python bitness:**
```powershell
python -c "import struct; print('64-bit' if struct.calcsize('P') == 8 else '32-bit')"
```

---

### Step 2: Run the Installer

1. **Double-click** `osgeo4w-setup-x86_64.exe`
2. You'll see a welcome dialog; click **Next**
3. Choose installation type:
   - Select **"Advanced Install"** (not "Express")
   - Click **Next**

---

### Step 3: Choose Installation Folder

- **Default folder**: `C:\OSGeo4W64\` (recommended — keep the default)
- Click **Next**

---

### Step 4: Select Local Package Directory

- Keep the default (usually `C:\OSGeo4W64\` download folder)
- Click **Next**

---

### Step 5: Choose Connection Type

- Select **"Direct connection"** (unless behind a proxy)
- Click **Next**

---

### Step 6: Choose Download Site

- Select any mirror (e.g., **http://download.osgeo.org** or **http://appel.gis-lab.info**)
- Click **Next**
- The installer will download the package list

---

### Step 7: **CRITICAL** — Select Packages

You'll see a tree of categories. Look for and expand:

**Expand `Libs` category:**
- Find **`gdal`** → Click on it until it shows a version number (e.g., `gdal-3.7.0`)
- Find **`python3-gdal`** → Click on it until it shows a version number

**Example: After clicking, you should see:**
```
Libs
  ├─ gdal                    [3.7.0-0 ✓]  ← Version shows, will be installed
  ├─ python3-gdal           [3.7.0-0 ✓]  ← Version shows, will be installed
  └─ (other libs)
```

**Optional but recommended:**
- Also install **`proj`** (for coordinate transformations)
- Also install **`geos`** (for geometry operations)

**Do NOT install** the full QGIS unless you want the GUI (it's large).

Click **Next** once you've selected these packages.

---

### Step 8: Accept Licenses & Install

- Review and accept any license dialogs
- The installer will download and install GDAL, Python bindings, and dependencies
- This may take 5–10 minutes depending on your internet speed
- You'll see a progress window

---

### Step 9: Finish

- Click **Finish**
- The installer will complete and may ask to create a desktop shortcut (optional)

---

## Step 10: Verify Installation

Open **PowerShell** and run:

```powershell
# Test 1: Check if GDAL is in system PATH
gdalinfo --version
```

Expected output:
```
GDAL 3.7.0, released 2023/11/06
```

If this **fails** ("gdalinfo not found"), continue to Step 11.

```powershell
# Test 2: Check if Python can import GDAL
python -c "from osgeo import ogr, gdal; print('GDAL version:', gdal.__version__)"
```

Expected output:
```
GDAL version: 3.7.0
```

If both tests pass, **✓ GDAL is installed correctly!**

---

## Step 11: Fix Python Path (if needed)

If Python import fails, you need to add OSGeo4W to your Python path:

### Option A: Add to Python sys.path (easiest)

Create a file `setup_gdal.py` in your project:

```python
import sys
import os

# Add OSGeo4W to Python path
osgeo_path = r'C:\OSGeo4W64\bin'
python_packages = r'C:\OSGeo4W64\apps\Python310\lib\site-packages'

if osgeo_path not in sys.path:
    sys.path.insert(0, osgeo_path)
if python_packages not in sys.path:
    sys.path.insert(0, python_packages)

# Now test
from osgeo import ogr, gdal
print(f"✓ GDAL {gdal.__version__} loaded successfully")
```

Then in your code (or at the start of `tools/noaa_enc_loader.py`), do:
```python
import setup_gdal
```

### Option B: Set environment variable (permanent)

1. Press **Win + R**, type `sysdm.cpl`, press Enter
2. Go to **"Advanced"** tab → **"Environment Variables"** button
3. Under "User variables", click **New**:
   - Variable name: `PYTHONPATH`
   - Variable value: `C:\OSGeo4W64\apps\Python310\lib\site-packages`
4. Click OK, restart Python

---

## Step 12: Install Python Packages (Fiona, Shapely)

Once GDAL works, install companion libraries:

```powershell
pip install fiona shapely pyproj
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `gdalinfo: command not found` | OSGeo4W bin folder not in PATH; see Step 11 Option B |
| `ModuleNotFoundError: No module named 'osgeo'` | Python packages not installed; see Step 11 Option A or B |
| Installer downloads very slowly | Change mirror site in Step 6 |
| Installer crashes during download | Disable antivirus temporarily, try again |
| Multiple Python versions installed | Ensure you're using the correct Python interpreter |

---

## Verify Everything Works

Once installation is complete, test the ENC loader:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"

# Download a test chart first from https://www.charts.noaa.gov/ENCs/ENCs.shtml
# Place in: bridge_sim/areas/noaa_charts/US5VA18M.000

python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

Expected output:
```
[ENC] Opened: US5VA18M.000
[ENC] Layers available: 45
[ENC] Layer 0: LNDSRF (1234 features)
...
[ENC] Bounds: lat=37.50..36.00, lon=-75.30..-74.50
[ENC] Exported ... features to chart_export.geojson
✓ ENC chart loaded and exported successfully!
```

---

## Next Steps After GDAL Installation

1. Download a test NOAA ENC chart
2. Run the loader test (above)
3. Let me know the output
4. I'll integrate ENC rendering into the ECDIS display

---

## Quick Reference: OSGeo4W Folder Structure

```
C:\OSGeo4W64\
  ├── bin/                    ← Contains gdalinfo, gdal tools
  ├── apps/
  │   └── Python310/          ← Python with GDAL bindings
  │       └── lib/
  │           └── site-packages/  ← osgeo module here
  └── share/
      └── gdal/               ← Data files (projections, etc.)
```

If you can't find these folders, re-run the installer and check the installation path (default: C:\OSGeo4W64\).

---

**Once you complete the above and can run the test, let me know and I'll add ENC rendering to your ECDIS!**
