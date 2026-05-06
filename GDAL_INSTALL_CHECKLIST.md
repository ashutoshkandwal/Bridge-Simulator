# OSGeo4W Installation Checklist

Your system check shows:
- ✓ Python 3.10.6 (64-bit) — correct
- ✗ GDAL not installed

## Follow These Steps (10-15 minutes)

### ✓ Step 1: Download OSGeo4W Installer

1. Open browser: https://trac.osgeo.org/osgeo4w/
2. Look for the large download button
3. Click **osgeo4w-setup-x86_64.exe** (64-bit version)
   - Save to: `Downloads` folder
4. Wait for download to complete (~10 MB)

**✓ Check**: You have `osgeo4w-setup-x86_64.exe` in Downloads

---

### ✓ Step 2: Run Installer

1. **Double-click** `osgeo4w-setup-x86_64.exe`
2. Windows may ask "Do you want to allow this app to make changes?" → Click **Yes**
3. Wait for the installer window to open

**✓ Check**: Installer window appears with "Welcome to OSGeo4W Setup"

---

### ✓ Step 3: Choose Installation Type

Installer screen: "Choose a Setup Type"
- ⭕ Express (fast, installs defaults)
- ⭕ **Advanced Install** ← **SELECT THIS**

Click **Next >**

**✓ Check**: You clicked "Advanced Install"

---

### ✓ Step 4: Installation Directory

Screen: "Choose Installation Directory"
- Path shows: `C:\OSGeo4W64\` (or similar)
- **Leave it as default** (do not change)

Click **Next >**

**✓ Check**: Installation directory is `C:\OSGeo4W64\`

---

### ✓ Step 5: Local Package Directory

Screen: "Select Local Package Directory"
- Choose any folder (default is fine)
- This is just where files download temporarily

Click **Next >**

---

### ✓ Step 6: Internet Connection

Screen: "Select Connection Type"
- ⭕ **Direct Connection** ← **SELECT THIS**

Click **Next >**

**✓ Check**: "Direct Connection" selected

---

### ✓ Step 7: Choose Download Mirror

Screen: "Select Download Site"
- Choose any mirror (e.g., **http://download.osgeo.org**)
- If one is slow, you can pick another

Click **Next >**

Installer will now download package list (wait 30 seconds)

---

### ✓ Step 8: SELECT PACKAGES (CRITICAL!)

Screen shows a tree view with many categories.

**You MUST select these:**

1. Expand **Libs** category by clicking the `+` icon
2. Find `gdal` in the list
   - Click the word "Skip" next to it until it shows a version (e.g., `gdal-3.7.0`)
   - Once clicked, it should show the version number instead of "Skip"
3. Find `python3-gdal` in the list
   - Click the word "Skip" next to it until it shows a version (e.g., `python3-gdal-3.7.0`)

**Optional (nice-to-have):**
- Also find and click `proj` (Projections library)
- Also find and click `geos` (Geometry operations)

**Screenshot reference:**
```
[+] Libs
    ├─ [ ] boost
    ├─ [ ] cpp-netcdf
    ├─ [✓] gdal                 ← Version shows (3.7.0-1 or similar)
    ├─ [ ] geos
    ├─ [ ] libtiff
    ├─ [✓] python3-gdal         ← Version shows (3.7.0-1 or similar)
    ├─ [ ] python3-fiona
    └─ ...
```

Once you see version numbers (not "Skip"), you're ready.

Click **Next >**

**✓ Check**: You see version numbers next to `gdal` and `python3-gdal`

---

### ✓ Step 9: Accept Licenses

Screen shows license text.
- Read and accept (click buttons as prompted)
- Usually just a few clicks

Click **I Agree** or **Accept**

---

### ✓ Step 10: Installation Progress

Installer downloads and installs packages (~200–500 MB).
- **This will take 5–10 minutes** depending on your internet
- Watch the progress bar
- **Do NOT close the window**

**✓ Check**: Progress bar reaches 100%

---

### ✓ Step 11: Installation Complete

Screen: "Installation Complete"
- May offer to create desktop shortcut (optional)

Click **Finish**

Windows may close the installer window automatically.

**✓ Check**: Installer closed, you're back at desktop

---

## Step 12: Verify Installation

Open **PowerShell** and run:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python setup_gdal.py --verbose
```

**Expected output if successful:**
```
✓ SUCCESS: GDAL is ready to use!
```

**If still failing**, try:
```powershell
python setup_gdal.py --verbose 2>&1 | head -20
```

---

## If Installation Fails

**Issue**: Installer won't open
- Try running as Administrator (right-click → Run as administrator)

**Issue**: Package download is very slow
- Change mirror in Step 7 to a different one
- Or download manually from http://download.osgeo.org/osgeo4w/

**Issue**: After install, still "GDAL not found"
- Close PowerShell and open a **NEW** PowerShell window
- Try again (Windows needs to refresh PATH)
- If still no luck, try: `python setup_gdal.py` without --verbose

---

## Once Installation Succeeds

Run this to test the ENC loader:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"

# First, download a test chart from:
# https://www.charts.noaa.gov/ENCs/ENCs.shtml
# Save to: bridge_sim/areas/noaa_charts/US5VA18M.000

python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

Expected output:
```
[ENC] Opened: US5VA18M.000
[ENC] Layers available: 45
...
✓ ENC chart loaded successfully!
```

---

## After You Complete These Steps

1. Run setup_gdal.py verification
2. Let me know if it says "✓ SUCCESS"
3. Then I'll integrate ENC rendering into your ECDIS

**You're almost there! 🎯**
