# OSGeo4W Installer: Download Site Selection

## Current Step

You're at: **"Select Download Site"** screen

This is STEP 6 of the installation. You're on track! ✓

---

## What to Do

The installer is asking: "Which website should I download packages from?"

### Option: Just Pick Any Mirror

The screen shows a list of URLs like:
- `http://download.osgeo.org`
- `http://appel.gis-lab.info`
- `http://mirror.umd.edu`
- etc.

**Action**: 
1. Click on any URL in the list (e.g., **http://download.osgeo.org**)
2. It will be highlighted/selected
3. Click **Next >**

The installer will then download the package list from that mirror.

---

## If Downloads Are Slow

If the first mirror is slow:
- Note the URL at the top of the list
- Try a different one from the list
- Click **Next >** again
- If still slow, you can stop and try a different mirror

---

## Expected Next Steps

After you click **Next >**:
1. Installer downloads package list (wait ~30 seconds)
2. You'll see a tree view with categories (Libs, Devel, etc.)
3. **IMPORTANT**: Expand `Libs` and select:
   - `gdal`
   - `python3-gdal`
   - (See `GDAL_INSTALL_CHECKLIST.md` Step 8 for details)

---

## Summary

✓ You're at the right place  
✓ Just pick any mirror from the list  
✓ Click **Next >**  
✓ Continue to the package selection screen

**Once you see the Libs tree, refer back to `GDAL_INSTALL_CHECKLIST.md` Step 8!**
