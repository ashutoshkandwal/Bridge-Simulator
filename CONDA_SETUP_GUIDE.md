# Install Miniconda and GDAL with Conda (Windows 10)

Your OSGeo4W installation isn't connecting to Python properly. **Conda is faster and more reliable** for GDAL on Windows.

## Step 1: Download Miniconda (2 min)

1. Open browser: https://docs.conda.io/en/latest/miniconda.html
2. Download: **Miniconda3 Windows 64-bit** (look for the `.exe` file)
3. Save to Downloads folder
4. Double-click to run installer

---

## Step 2: Install Miniconda (5 min)

Installer screens:
1. **Welcome** → Click **Next**
2. **License** → Read, click **I Agree**
3. **Installation Type** → Choose **"Just Me"** (not "All Users")
4. **Installation Location** → Accept default (usually `C:\Users\<username>\miniconda3`)
5. **Advanced Options** → 
   - ☐ Uncheck: "Add Miniconda3 to PATH" (we'll do this manually)
   - ☑ Check: "Register Miniconda3 as my default Python 3.10"
6. Click **Install** → Wait for progress bar

Once finished, click **Next** → **Finish**

**Restart your computer** (important for PATH updates)

---

## Step 3: Open New PowerShell & Create GDAL Environment (5 min)

After restart, open **PowerShell** and run these commands (copy-paste each line):

```powershell
# Verify Miniconda installed
conda --version

# Create a new environment with GDAL and geospatial tools
conda create -n gdal_env python=3.10 gdal fiona shapely pyproj -c conda-forge -y

# Activate the environment
conda activate gdal_env

# Verify GDAL is working
python -c "from osgeo import gdal; print('GDAL version:', gdal.__version__)"
```

**Expected output** after the last command:
```
GDAL version: 3.7.0
```

If you see this, **GDAL is installed successfully!** ✓

---

## Step 4: Test the ENC Loader (Optional)

Once GDAL env is activated, download a test chart and run:

```powershell
# Make sure gdal_env is still active (you should see (gdal_env) in your prompt)

cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"

# Download a test NOAA chart first, place in bridge_sim/areas/noaa_charts/US5VA18M.000

python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

---

## Step 5: Use the GDAL Environment for Your Simulator

When you want to use the simulator or ENC tools:

```powershell
# Activate the GDAL environment
conda activate gdal_env

# Go to your project
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"

# Run simulator
python -m bridge_sim.main

# Or test ENC loader
python tools/noaa_enc_loader.py "bridge_sim/areas/noaa_charts/US5VA18M.000"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `conda: command not found` | Restart PowerShell completely; Miniconda PATH needs refresh |
| `GDAL version: ...` doesn't print | Make sure you ran `conda activate gdal_env` first |
| Download very slow | Try again later or use a different internet connection |

---

## How Conda Works

- **Environments** = isolated Python + package folders (like venv, but better)
- **conda activate gdal_env** = switches your PowerShell to use the gdal_env Python (3.10 + GDAL + deps)
- **conda deactivate** = switches back to system Python (if needed)
- You can have many environments; switch between them easily

---

## Next Steps

1. Download Miniconda from https://docs.conda.io/en/latest/miniconda.html
2. Run the installer (follow Step 1–2 above)
3. Restart computer
4. Open PowerShell, run the commands in Step 3
5. When you see `GDAL version: ...`, let me know and I'll integrate ENC charts into your ECDIS!

---

**Total time: ~15 minutes. Worth it for reliable GDAL support!** ✓
