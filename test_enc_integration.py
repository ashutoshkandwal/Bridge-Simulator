#!/usr/bin/env python3
"""
Quick test to verify ECDIS ENC integration.

If you have a sample NOAA ENC chart (.000 or .gpkg file), this will:
1. Verify the ENC loader can import
2. Try to load and parse a sample chart
3. Print available layers and bounds

Run from the project root:
    python test_enc_integration.py [path/to/chart.000]

Or just:
    python test_enc_integration.py

to see available test paths.
"""

import sys
import os

def main():
    # Check for GDAL availability
    try:
        from osgeo import gdal
        print(f"✓ GDAL {gdal.__version__} available")
    except ImportError as e:
        print(f"✗ GDAL not available: {e}")
        print(f"  Install with: conda install -n gdal_env gdal -c conda-forge -y")
        return 1
    
    # Check for ENC loader
    try:
        from tools.noaa_enc_loader import ENChart
        print("✓ ENC loader module available")
    except ImportError as e:
        print(f"✗ ENC loader not available: {e}")
        return 1
    
    # Check for ECDIS integration
    try:
        from bridge_sim.ecdis import ECDISDisplay
        print("✓ ECDIS ENC integration available")
        
        # Check if load_noaa_enc method exists
        if hasattr(ECDISDisplay, 'load_noaa_enc'):
            print("  - load_noaa_enc() method: YES")
        if hasattr(ECDISDisplay, 'draw_enc_layers'):
            print("  - draw_enc_layers() method: YES")
    except ImportError as e:
        print(f"✗ ECDIS not available: {e}")
        return 1
    
    # Try to load a sample chart if provided
    if len(sys.argv) > 1:
        chart_path = sys.argv[1]
        if os.path.exists(chart_path):
            print(f"\nLoading chart: {chart_path}")
            try:
                chart = ENChart(chart_path)
                bounds = chart.get_bounds()
                print(f"  Bounds: {bounds}")
                print(f"  Layers: {list(chart.layers.keys())}")
                print("✓ Chart loaded successfully!")
                return 0
            except Exception as e:
                print(f"✗ Failed to load chart: {e}")
                return 1
        else:
            print(f"✗ File not found: {chart_path}")
            return 1
    else:
        print("\nNo chart path provided.")
        print("\nTo test with a real NOAA ENC chart:")
        print("  1. Download a sample from: https://www.charts.noaa.gov/ENCs/ENCs.shtml")
        print("  2. Place the .000 file in: bridge_sim/areas/noaa_charts/")
        print("  3. Run: python test_enc_integration.py bridge_sim/areas/noaa_charts/<chart>.000")
        return 0

if __name__ == '__main__':
    sys.exit(main())
