"""
Quick Start: Web ECDIS Viewer

This script launches just the web ECDIS viewer with demo ship movement.
Use this to test the viewer independently of the full simulator.

Usage:
    conda run -n gdal_env python run_web_ecdis.py
    
Then open: http://127.0.0.1:5000
"""
import os
import sys

# Add project root and web directory to path
project_root = os.path.dirname(__file__)
web_dir = os.path.join(project_root, 'web')
sys.path.insert(0, web_dir)

# Change to web directory so static files are served correctly
os.chdir(web_dir)

# Run the standalone server (includes demo ship movement)
if __name__ == '__main__':
    from server import run_server
    run_server(host='127.0.0.1', port=5000, debug=False)
