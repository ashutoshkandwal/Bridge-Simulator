# Quick Commands to Run Now

Copy and paste each command into PowerShell one at a time. Press Enter after each.

## Command 1: Verify Conda
```powershell
conda --version
```

**Expected:** Shows a version like `conda 24.1.2`

---

## Command 2: Create GDAL Environment
```powershell
conda create -n gdal_env python=3.10 gdal fiona shapely pyproj -c conda-forge -y
```

**Expected:** Takes 3–5 minutes. You'll see downloading/linking progress. Wait until you see:
```
done
# To activate this environment, use
# $ conda activate gdal_env
```

---

## Command 3: Activate Environment
```powershell
conda activate gdal_env
```

**Expected:** Prompt changes to show `(gdal_env)` at the start:
```
(gdal_env) PS C:\Users\...>
```

---

## Command 4: Verify GDAL Works
```powershell
python -c "from osgeo import gdal; print('GDAL version:', gdal.__version__)"
```

**Expected:** Prints something like:
```
GDAL version: 3.7.0
```

---

## If All 4 Commands Show Expected Output

Reply: **"GDAL verified! Ready to integrate ENC charts"**

Then I'll add ENC support to your ECDIS! 🎉

---

## If Any Command Fails

Copy the error message and paste it here, and I'll help troubleshoot.

---

**Run these now!** →
