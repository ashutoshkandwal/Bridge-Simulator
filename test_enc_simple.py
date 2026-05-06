#!/usr/bin/env python3
"""
Quick test of ENC loader without pygame dependency.
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
        return 1
    
    # Check for dependencies
    try:
        import fiona
        print("✓ Fiona available")
    except ImportError:
        print("✗ Fiona not available")
    
    try:
        import shapely
        print("✓ Shapely available")
    except ImportError:
        print("✗ Shapely not available")
    
    # Check for ENC loader
    try:
        from tools.noaa_enc_loader import ENChart
        print("✓ ENC loader module available")
    except ImportError as e:
        print(f"✗ ENC loader not available: {e}")
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
        print("  3. Run: python tools/noaa_enc_loader.py bridge_sim/areas/noaa_charts/<chart>.000")
        return 0

if __name__ == '__main__':
    sys.exit(main())
