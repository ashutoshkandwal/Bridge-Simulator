# Miniconda Installation Checklist & Commands

## While Downloading...

**Expected:** Miniconda3 Windows 64-bit `.exe` file (~60 MB)  
**Download time:** 2–5 minutes (depends on internet)  
**Save location:** `Downloads` folder

---

## Installation Checklist (After Download Complete)

### ☐ Step 1: Run Installer
- Double-click the `.exe` file
- Windows may ask "Allow this app to make changes?" → Click **Yes**
- Wait for installer window to open

### ☐ Step 2: Choose "Just Me"
- Screen: "Installation Type"
- Select: **Just Me** (not "All Users")
- Click **Next**

### ☐ Step 3: Accept Installation Path
- Screen: "Installation Location"
- Path shows: `C:\Users\<your-username>\miniconda3`
- Accept default (click **Next**)

### ☐ Step 4: Advanced Options
- Screen: "Advanced Options"
- **Uncheck**: "Add Miniconda3 to PATH" ☐
- **Check**: "Register Miniconda3 as my default Python 3.10" ☑
- Click **Next**

### ☐ Step 5: Install
- Click **Install**
- Watch progress bar (takes 1–2 minutes)
- Do NOT close the window

### ☐ Step 6: Complete
- Screen: "Installation Complete"
- Click **Next** then **Finish**
- Close installer

### ☐ Step 7: RESTART COMPUTER
- **CRITICAL**: Save all work and restart Windows
- (PowerShell needs PATH refresh)

---

## After Restart: Create GDAL Environment

### ☐ Step 8: Open New PowerShell

1. Click **Start** menu
2. Type: `powershell`
3. Click **Windows PowerShell**
4. New window opens

### ☐ Step 9: Verify Conda Installed

Copy this command and paste into PowerShell:

```powershell
conda --version
```

**Expected output:**
```
conda 24.1.2 (or similar version number)
```

If you see a version number, conda is ready! ✓

---

## ☐ Step 10: Create GDAL Environment

Copy each command below, paste into PowerShell, press Enter. Do one at a time:

### Command 1: Create environment
```powershell
conda create -n gdal_env python=3.10 gdal fiona shapely pyproj -c conda-forge -y
```

**What happens:** Conda downloads and installs GDAL + dependencies (this takes 3–5 minutes). You'll see progress output. Don't interrupt!

**Expected ending:**
```
done
#
# To activate this environment, use
#
#     $ conda activate gdal_env
```

### Command 2: Activate environment
```powershell
conda activate gdal_env
```

**What you should see:** Prompt changes to:
```
(gdal_env) PS C:\Users\<username>>
```

The `(gdal_env)` at the start means you're in the GDAL environment. ✓

### Command 3: Verify GDAL Works
```powershell
python -c "from osgeo import gdal; print('GDAL version:', gdal.__version__)"
```

**Expected output:**
```
GDAL version: 3.7.0
```

(The version number might be different; that's OK as long as you see a version!)

If you see `GDAL version: ...` → **SUCCESS!** ✓

---

## ☐ Step 11: Test ENC Loader (Optional)

Once GDAL environment is active:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python tools/noaa_enc_loader.py --help
```

This should print help text for the ENC loader.

---

## ☐ Step 12: Run Your Simulator

With `gdal_env` still active:

```powershell
cd "e:\PYTHON\Radar simulator\bridge_sim_configurable"
python -m bridge_sim.main
```

Should launch the simulator menu! 🎉

---

## Important Notes

- **Always activate before use:**
  ```powershell
  conda activate gdal_env
  ```
  (You'll see `(gdal_env)` in your prompt)

- **To deactivate** (return to system Python):
  ```powershell
  conda deactivate
  ```

- **Environment is permanent:** Once created, `gdal_env` stays on your computer. You can activate it anytime.

- **Don't run `conda init`** — it modifies PowerShell startup in ways that can conflict with other tools.

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| Download Miniconda | 2–5 min | ⏳ In progress |
| Install + Restart | 5 min | ⏹️ Waiting |
| Create env | 5 min | ⏹️ Waiting |
| Verify GDAL | 1 min | ⏹️ Waiting |
| **Total** | **~15 min** | — |

---

## When Done, Tell Me:

After you see `GDAL version: 3.7.0` (or similar), reply:

> "GDAL installed and working!"

Then I'll:
1. Integrate ENC chart loading into your ECDIS
2. Help you download a real NOAA chart
3. Get your simulator displaying professional vector charts!

---

**You're almost there! 🚀**
