"""
Web ECDIS Server

Serves the Leaflet-based ECDIS viewer and streams live ship position updates.

Usage:
    python web/server.py
    
    Then open: http://localhost:5000
"""
import os
import json
import time
import threading
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_sock import Sock

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Ship state (updated by the simulator)
ship_state = {
    # Defaults; will be overridden by /api/set_ship or update_ship_position
    'lat': 0.0,
    'lon': 0.0,
    'heading': 0.0,
    'speed': 0.0,
    'timestamp': time.time()
}

# Lock for thread-safe updates
ship_lock = threading.Lock()

# Connected WebSocket clients
ws_clients = []

@app.route('/')
def index():
    """Serve the ECDIS viewer HTML"""
    return send_from_directory('.', 'ecdis_viewer.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (Leaflet CSS/JS for offline use)"""
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    """Serve a favicon if present; otherwise return a tiny transparent SVG."""
    # Prefer a real favicon in static/images if available
    static_path = os.path.join('static', 'images')
    ico_path = os.path.join(static_path, 'favicon.ico')
    svg_path = os.path.join(static_path, 'favicon.svg')
    if os.path.exists(ico_path):
        return send_from_directory(static_path, 'favicon.ico')
    if os.path.exists(svg_path):
        return send_from_directory(static_path, 'favicon.svg')
    # Fallback: inline minimal transparent SVG
    svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"></svg>
    """.strip()
    return (svg, 200, {
        'Content-Type': 'image/svg+xml'
    })

@app.route('/chart_export.geojson')
def chart_geojson():
    """Serve the exported ENC GeoJSON"""
    # Look for the chart export in the parent directory
    chart_path = os.path.join('..', 'chart_export.geojson')
    if os.path.exists(chart_path):
        return send_from_directory('..', 'chart_export.geojson')
    else:
        return jsonify({'type': 'FeatureCollection', 'features': []}), 404

@app.route('/api/ship')
def get_ship():
    """REST endpoint for current ship position"""
    with ship_lock:
        return jsonify(ship_state)

@sock.route('/ws')
def websocket_handler(ws):
    """WebSocket endpoint for live ship updates"""
    print(f"[WS] New connection attempt...")
    ws_clients.append(ws)
    print(f"[WS] Client connected (total: {len(ws_clients)})")

    try:
        # Send initial state
        with ship_lock:
            initial = json.dumps({
                'type': 'ship_update',
                **ship_state
            })
            ws.send(initial)

        # Keep connection alive; don't force client to send messages
        while True:
            try:
                data = ws.receive(timeout=1.0)
                if data:
                    # No commands expected currently; reserved for future use
                    pass
            except TimeoutError:
                # Normal: no client message within timeout; keep connection open
                pass
            except Exception as e:
                # Likely a disconnect or network error
                print(f"[WS] Receive error: {e}")
                break
            time.sleep(0.01)
    except Exception as e:
        print(f"[WS] Connection error: {e}")
    finally:
        if ws in ws_clients:
            ws_clients.remove(ws)
        print(f"[WS] Client disconnected (total: {len(ws_clients)})")

def update_ship_position(lat, lon, heading, speed):
    """
    Update ship position and broadcast to all connected clients.
    
    Called by the simulator to push updates.
    """
    with ship_lock:
        ship_state['lat'] = lat
        ship_state['lon'] = lon
        ship_state['heading'] = heading
        ship_state['speed'] = speed
        ship_state['timestamp'] = time.time()
    
    # Broadcast to all WebSocket clients
    message = json.dumps({
        'type': 'ship_update',
        'lat': lat,
        'lon': lon,
        'heading': heading,
        'speed': speed,
        'timestamp': ship_state['timestamp']
    })
    
    # Debug log every 25 calls (~5 seconds)
    if not hasattr(update_ship_position, '_call_count'):
        update_ship_position._call_count = 0
    update_ship_position._call_count += 1
    if update_ship_position._call_count % 25 == 0:
        print(f"[ECDIS WS] Broadcasting to {len(ws_clients)} clients: LAT={lat:.5f}, LON={lon:.5f}")
    
    disconnected = []
    for ws in ws_clients:
        try:
            ws.send(message)
        except Exception as e:
            if update_ship_position._call_count % 25 == 0:
                print(f"[ECDIS WS] Send failed: {e}")
            disconnected.append(ws)
    
    # Clean up disconnected clients
    for ws in disconnected:
        if ws in ws_clients:
            ws_clients.remove(ws)

def run_server(host='127.0.0.1', port=5000, debug=False):
    """
    Start the Flask server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    print(f"[WEB] Starting ECDIS web server on http://{host}:{port}")
    print(f"[WEB] Open http://{host}:{port} in your browser to view the chart")
    app.run(host=host, port=port, debug=debug, use_reloader=False)

if __name__ == '__main__':
    # Standalone mode. Demo movement is DISABLED by default to avoid confusion.
    # To enable the circular demo, set environment variable ECDIS_DEMO=1 before running.
    enable_demo = os.environ.get('ECDIS_DEMO', '0') == '1'
    if enable_demo:
        import math

        def demo_ship():
            """Simulate ship movement for testing"""
            angle = 0
            center_lat = 38.13
            center_lon = -75.93
            radius = 0.05

            while True:
                lat = center_lat + radius * math.sin(angle)
                lon = center_lon + radius * math.cos(angle)
                heading = (angle * 180 / math.pi) % 360
                speed = 12.0

                update_ship_position(lat, lon, heading, speed)

                angle += 0.01
                time.sleep(0.1)

        # Start demo ship in background
        demo_thread = threading.Thread(target=demo_ship, daemon=True)
        demo_thread.start()

    # Run server
    run_server(debug=False)
