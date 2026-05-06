# Finding python3-gdal in OSGeo4W Installer

## Current Issue

You can see `gdal` but **`python3-gdal` is not visible** in the Libs list.

---

## Solution: Search for It

### Method 1: Use Search Box (Easiest)

1. Look for a **"Search"** box at the top of the installer window
2. Type: `python3-gdal`
3. Press Enter
4. The installer will filter to show matching packages
5. Click the word "Skip" next to `python3-gdal` until it shows a version number (e.g., `3.7.0-1`)

---

### Method 2: Look in Different Category

`python3-gdal` might be under a different category, not `Libs`. Try:

1. Look for these category names in the tree:
   - **Libs** (original location)
   - **Python** (if there's a separate Python category)
   - **Development** or **Devel**
   - **Geodata** or **Geospatial**

2. Expand each category by clicking the `+` icon
3. Look for `python3-gdal` or anything with "gdal" in the name

---

### Method 3: Uncheck "Hide Installed"

1. Look for a checkbox or filter option that says:
   - "Hide installed packages"
   - "Show all packages"
   - "Include installed"

2. **Uncheck** it (if checked)
3. This will show ALL available packages, including those already installed

---

### Method 4: Just Install `gdal` Alone (Workaround)

If you absolutely can't find `python3-gdal`:

1. **Select only `gdal`** (click "Skip" until version shows)
2. **Do NOT select anything else** (yet)
3. Click **Next >** and complete the installation
4. After installation, open **PowerShell** and run:

```powershell
pip install gdal
```

This installs the Python bindings via pip instead.

---

## Most Likely Cause

**`python3-gdal` is in the `Libs` category but the list is very long.**

Try:
1. Scroll **down** in the Libs list (there are many packages)
2. Look for `python3-*` entries
3. Or use Search for `gdal` to filter results

---

## Expected Result

Once you find and select both:
- `gdal` → shows version (e.g., `3.7.0-1`)
- `python3-gdal` → shows version (e.g., `3.7.0-1`)

Both should have a checkmark ✓ or version number visible (not "Skip").

Then click **Next >** to continue.

---

## If Still Stuck

1. Try **Search** first (Method 1) — this is most reliable
2. If search doesn't work, try **Uncheck "Hide Installed"** (Method 3)
3. As last resort, install via pip after OSGeo4W setup (Method 4)

**Let me know which method you use!**
