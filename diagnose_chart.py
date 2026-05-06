#!/usr/bin/env python3
"""
ECDIS Chart Loading Diagnostic
Verifies that your chart is properly set up and loading in ECDIS.
"""

import os
import sys
from pathlib import Path

def check_chart_file():
    """Check if chart file exists in areas folder"""
    print("=" * 60)
    print("1. CHECKING CHART FILE")
    print("=" * 60)
    
    areas_path = Path(__file__).parent / "bridge_sim" / "areas"
    chart_files = list(areas_path.glob("*.[pP][nN][gG]")) + list(areas_path.glob("*.[jJ][pP][gG]"))
    
    if not chart_files:
        print("❌ No chart files found in bridge_sim/areas/")
        print(f"   Path: {areas_path}")
        return False
    
    print(f"✓ Found {len(chart_files)} chart file(s):")
    for cf in chart_files:
        size_kb = cf.stat().st_size / 1024
        print(f"  • {cf.name} ({size_kb:.1f} KB)")
    return True

def check_ecdis_code():
    """Check if ECDIS code can find charts"""
    print("\n" + "=" * 60)
    print("2. CHECKING ECDIS CODE")
    print("=" * 60)
    
    try:
        from bridge_sim.ecdis import ECDISDisplay
        print("✓ ECDIS module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Cannot import ECDIS: {e}")
        return False

def check_chart_loading():
    """Test if chart actually loads in ECDIS"""
    print("\n" + "=" * 60)
    print("3. TESTING CHART LOADING")
    print("=" * 60)
    
    try:
        import pygame as pg
        from bridge_sim.ecdis import ECDISDisplay
        
        # Initialize pygame silently
        pg.init()
        screen = pg.display.set_mode((1100, 618))
        
        # Try to create ECDIS display
        print("Creating ECDIS display...")
        ecdis = ECDISDisplay(screen)
        
        if ecdis.chart_img is not None:
            print(f"✓ Chart loaded successfully!")
            print(f"  Status: {ecdis.chart_status}")
            return True
        else:
            print(f"❌ Chart failed to load")
            print(f"  Status: {ecdis.chart_status}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chart loading: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_simulator():
    """Check if simulator runs"""
    print("\n" + "=" * 60)
    print("4. CHECKING SIMULATOR")
    print("=" * 60)
    
    try:
        from bridge_sim.main import App
        print("✓ Simulator imports successfully")
        print("  Ready to run: python -m bridge_sim.main")
        return True
    except ImportError as e:
        print(f"❌ Cannot import simulator: {e}")
        return False

def print_summary(results):
    """Print final summary"""
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    checks = [
        ("Chart file exists", results[0]),
        ("ECDIS code OK", results[1]),
        ("Chart loads", results[2]),
        ("Simulator OK", results[3]),
    ]
    
    for check_name, result in checks:
        status = "✓" if result else "❌"
        print(f"{status} {check_name}")
    
    all_pass = all(results)
    print("\n" + "=" * 60)
    if all_pass:
        print("🎉 ALL CHECKS PASSED!")
        print("\nYour chart is ready to display in ECDIS!")
        print("\nTo see your chart:")
        print("  1. Run: python -m bridge_sim.main")
        print("  2. Enter your ship position")
        print("  3. Press SPACE twice to go to ECDIS")
        print("  4. Your chart will display! 🗺️")
    else:
        print("⚠️ Some checks failed. See details above.")
    print("=" * 60)
    
    return all_pass

def main():
    print("\n🔍 ECDIS CHART DIAGNOSTIC\n")
    
    results = [
        check_chart_file(),
        check_ecdis_code(),
        check_chart_loading(),
        check_simulator(),
    ]
    
    success = print_summary(results)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
