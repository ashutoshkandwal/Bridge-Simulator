"""
Standalone Web Radar Viewer

Launches the web-based radar display for testing without the full simulator.

Usage:
    python run_web_radar.py
    
    Then open: http://localhost:5001/radar in your browser
"""
import sys
import os

# Add the parent directory to path to import web modules
sys.path.insert(0, os.path.dirname(__file__))

from web.radar_server import run_radar_server

if __name__ == '__main__':
    print("=" * 60)
    print("MARINE RADAR WEB VIEWER - Standalone Mode")
    print("=" * 60)
    print()
    print("This will start the radar web server with demo data.")
    print("The radar will show simulated sea clutter and targets.")
    print()
    print("Controls:")
    print("  - Range +/- buttons to change radar range")
    print("  - NORTH UP / COURSE UP mode toggle")
    print("  - RELATIVE / TRUE MOTION toggle")
    print("  - GAIN, SEA, RAIN sliders for clutter control")
    print("  - EBL/VRM measurement tools")
    print("  - TX ON/STBY to enable/disable transmission")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        run_radar_server(host='127.0.0.1', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
