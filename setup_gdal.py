#!/usr/bin/env python
"""
GDAL Setup & Verification Script

This script attempts to:
1. Locate OSGeo4W or system GDAL installation
2. Add paths to sys.path
3. Test GDAL import
4. Report version and capabilities

Run this before using the NOAA ENC loader.

Usage:
    python setup_gdal.py
    python setup_gdal.py --verbose
    python setup_gdal.py --check-only

"""
import sys
import os
import platform
import subprocess


def find_osgeo4w():
    """Search for OSGeo4W installation on Windows."""
    common_paths = [
        r'C:\OSGeo4W64',
        r'C:\OSGeo4W',
        r'C:\Program Files\OSGeo4W64',
        r'C:\Program Files\OSGeo4W',
    ]
    
    for path in common_paths:
        if os.path.isdir(path):
            return path
    
    return None


def check_gdal_command_line():
    """Test if gdalinfo is available in PATH."""
    try:
        result = subprocess.run(['gdalinfo', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return None


def check_python_gdal():
    """Test if Python can import GDAL."""
    try:
        from osgeo import gdal, ogr
        return gdal.__version__
    except ImportError:
        return None


def add_osgeo_to_path(osgeo_path, verbose=False):
    """Add OSGeo4W paths to sys.path and environment."""
    if not os.path.isdir(osgeo_path):
        if verbose:
            print(f"[WARN] OSGeo4W path not found: {osgeo_path}")
        return False
    
    # Common Python versions installed by OSGeo4W
    python_versions = ['Python310', 'Python39', 'Python311']
    
    for pyver in python_versions:
        site_packages = os.path.join(osgeo_path, 'apps', pyver, 'lib', 'site-packages')
        if os.path.isdir(site_packages):
            if verbose:
                print(f"[INFO] Found {pyver} site-packages: {site_packages}")
            sys.path.insert(0, site_packages)
            
            bin_path = os.path.join(osgeo_path, 'bin')
            if os.path.isdir(bin_path):
                sys.path.insert(0, bin_path)
                if verbose:
                    print(f"[INFO] Added to sys.path: {bin_path}")
            
            return True
    
    if verbose:
        print(f"[WARN] No compatible Python found in {osgeo_path}")
    return False


def main():
    """Main verification routine."""
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    check_only = '--check-only' in sys.argv
    
    print("=" * 70)
    print("GDAL Setup & Verification")
    print("=" * 70)
    
    # Platform info
    print(f"\n[INFO] Platform: {platform.system()} {platform.release()}")
    print(f"[INFO] Python: {sys.version.split()[0]} ({sys.executable})")
    
    # Check Python bitness
    import struct
    bitness = '64-bit' if struct.calcsize('P') == 8 else '32-bit'
    print(f"[INFO] Python bitness: {bitness}")
    
    # Test 1: Check command-line GDAL
    print("\n[TEST 1] Checking gdalinfo in PATH...")
    gdal_version_cli = check_gdal_command_line()
    if gdal_version_cli:
        print(f"  ✓ gdalinfo found: {gdal_version_cli}")
    else:
        print("  ✗ gdalinfo not found in PATH")
    
    # Test 2: Check Python GDAL (before path modifications)
    print("\n[TEST 2] Checking Python GDAL import (before path setup)...")
    gdal_version_py = check_python_gdal()
    if gdal_version_py:
        print(f"  ✓ GDAL Python already available: {gdal_version_py}")
        print("  → You can skip setup and use ENC loader directly!")
        return 0
    else:
        print("  ✗ GDAL Python not found; attempting to locate OSGeo4W...")
    
    # Test 3: Find and add OSGeo4W to path
    if platform.system() == 'Windows':
        print("\n[TEST 3] Locating OSGeo4W...")
        osgeo_path = find_osgeo4w()
        
        if osgeo_path:
            print(f"  ✓ Found OSGeo4W at: {osgeo_path}")
            
            if not check_only:
                print("\n[SETUP] Adding OSGeo4W to sys.path...")
                success = add_osgeo_to_path(osgeo_path, verbose=verbose)
                
                if success:
                    print("  ✓ OSGeo4W paths added to sys.path")
                    
                    # Test again after path modification
                    print("\n[TEST 4] Re-checking Python GDAL import (after setup)...")
                    gdal_version_py = check_python_gdal()
                    if gdal_version_py:
                        print(f"  ✓ GDAL Python now available: {gdal_version_py}")
                        print("\n" + "=" * 70)
                        print("✓ SUCCESS: GDAL is ready to use!")
                        print("=" * 70)
                        return 0
                    else:
                        print("  ✗ GDAL still not importable after path setup")
                else:
                    print("  ✗ Failed to add OSGeo4W paths")
        else:
            print("  ✗ OSGeo4W not found in common locations")
            print("\n  To install OSGeo4W:")
            print("    1. Download from: https://trac.osgeo.org/osgeo4w/")
            print("    2. Run osgeo4w-setup-x86_64.exe (for 64-bit Python)")
            print("    3. Select 'Advanced Install'")
            print("    4. Choose Libs → gdal, gdal-python")
            print("    5. Complete installation")
            print("    6. Re-run this script")
    else:
        print("\n[INFO] Non-Windows platform detected")
        print("  Install GDAL using your system package manager:")
        print("    Linux (Ubuntu/Debian): sudo apt-get install gdal-bin python3-gdal")
        print("    macOS: brew install gdal")
    
    print("\n" + "=" * 70)
    print("✗ GDAL setup incomplete. Please install OSGeo4W and try again.")
    print("=" * 70)
    return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
