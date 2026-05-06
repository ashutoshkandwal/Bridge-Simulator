"""
Export ENC chart to GeoJSON for bridge 3D view land rendering.

This script finds the available ENC chart and exports it to chart_export.geojson
in the project root, making land features visible in the bridge view.
"""
import os
import sys

# Find ENC chart file
enc_path = None
search_paths = [
    'bridge_sim/areas/noaa_charts/US4MD20M.000',
    'bridge_sim/areas/noaa_charts/*.000',
]

for path_pattern in search_paths:
    if '*' in path_pattern:
        import glob
        matches = glob.glob(path_pattern)
        if matches:
            enc_path = matches[0]
            break
    elif os.path.exists(path_pattern):
        enc_path = path_pattern
        break

if not enc_path:
    print("ERROR: No ENC chart found in bridge_sim/areas/noaa_charts/")
    print("Please ensure you have an ENC .000 file in that directory.")
    sys.exit(1)

print(f"Found ENC chart: {enc_path}")

# Export to GeoJSON
try:
    from tools.noaa_enc_loader import ENChart
    
    print(f"Loading chart from {enc_path}...")
    chart = ENChart(enc_path)
    
    output_path = 'chart_export.geojson'
    print(f"Exporting to {output_path}...")
    chart.export_to_geojson(output_path)
    
    print(f"✓ SUCCESS: Chart exported to {output_path}")
    print(f"✓ Land features (LNDARE) should now be visible in bridge view")
    print(f"\nReload the bridge view at: http://localhost:5001/bridge3d")
    
except Exception as e:
    print(f"ERROR: Failed to export chart: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
