"""
Web Radar Server

Serves the canvas-based radar viewer and streams live radar data.

Usage:
    python web/radar_server.py
    
    Then open: http://localhost:5001/radar
"""
import os
import json
import time
import threading
import math
import random
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sock import Sock

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Radar state (updated by the simulator)
radar_state = {
    'ship': {
        'x': 300,
        'y': 300,
        'heading': 0,
        'speed': 10,
        # Track geodetic position when provided by menu/API
        'lat': 38.15,  # Chesapeake Bay - positioned offshore with land visible
        'lon': -75.60,  # East side, in open water
    },
    'targets': [
        # Demo targets positioned ~3nm ahead for realistic 3D view distance
        {'id': 0, 'x': 305, 'y': 120, 'course': 180, 'speed': 12, 'lat': 38.20, 'lon': -75.600, 'vessel_type': 'nuc'},          # NUC vessel - dead ahead, ~3nm
        {'id': 1, 'x': 340, 'y': 130, 'course': 135, 'speed': 8, 'lat': 38.198, 'lon': -75.593, 'vessel_type': 'ram'},           # RAM vessel - 30° starboard, ~3nm
        {'id': 2, 'x': 270, 'y': 130, 'course': 225, 'speed': 15, 'lat': 38.198, 'lon': -75.607, 'vessel_type': 'cbd'}         # CBD vessel - 30° port, ~3nm
    ],
    'clutter': [],
    'range_nm': 12.0,
    'ppi_radius': 250,
    'mode': 'NORTH UP',
    'motion': 'RM',
    'north_up': True,
    'fixed_heading': 0,
    'tx_on': True,
    'range_rings': False,
    'ebl_visible': False,
    'ebl_bearing': 45.0,
    'vrm_visible': False,
    'vrm_radius': 2.0,
    'gain': 30,
    'sea': 0,
    'rain': 5,
    # Environmental inputs
    'wind_dir': 0.0,   # degrees True (wind FROM direction)
    'wind_speed': 0.0, # knots
    'timestamp': time.time()
}

# Bridge control state (updated by the simulator)
bridge_state = {
    'heading': 0.0,
    'speed': 0.0,
    'rpm': 0,
    'rot': 0.0,  # Rate of turn in degrees/minute
    'rudder_angle': 0.0,  # -35 to +35 degrees
    'telegraph': 'STOP',
    'motor1': 'STANDBY',
    'motor2': 'STANDBY',
    'timestamp': time.time()
}

# Lock for thread-safe updates
radar_lock = threading.Lock()
bridge_lock = threading.Lock()

# Connected WebSocket clients
radar_ws_clients = []
bridge_ws_clients = []

# Range presets (NM)
RANGES = [0.25, 0.5, 0.75, 1.5, 3.0, 6.0, 12.0, 24.0, 48.0]

@app.route('/')
def main_menu():
    """Serve the main menu/launcher page"""
    web_dir = os.path.dirname(__file__)
    return send_from_directory(web_dir, 'index.html')

@app.route('/radar')
def radar_index():
    """Serve the radar viewer HTML"""
    web_dir = os.path.dirname(__file__)
    return send_from_directory(web_dir, 'radar_viewer.html')

@app.route('/bridge3d')
def bridge3d_demo():
    """Serve the 3D bridge demo HTML"""
    web_dir = os.path.dirname(__file__)
    return send_from_directory(web_dir, 'bridge3d_demo.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/radar')
def get_radar():
    """REST endpoint for current radar state"""
    with radar_lock:
        return jsonify(radar_state)

@app.route('/api/chart_features')
def get_chart_features():
    """Extract land features from chart GeoJSON for radar echoes"""
    try:
        import json
        chart_path = os.path.join(os.path.dirname(__file__), '..', 'chart_export.geojson')
        
        if not os.path.exists(chart_path):
            return jsonify({'status': 'error', 'message': 'Chart file not found'}), 404
        
        # Parse GeoJSON and extract land/coastline features
        land_features = []
        
        with open(chart_path, 'r', encoding='utf-8') as f:
            chart_data = json.load(f)
        
        # Extract only LNDARE (land areas shown as yellow on chart)
        target_layers = ['LNDARE']
        
        for feature in chart_data.get('features', []):
            layer = feature.get('properties', {}).get('layer', '')
            if layer in target_layers:
                geom = feature.get('geometry', {})
                geom_type = geom.get('type', '')
                coords = geom.get('coordinates', [])
                
                # Only process polygons and linestrings
                if geom_type in ['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString']:
                    land_features.append({
                        'layer': layer,
                        'type': geom_type,
                        'coordinates': coords
                    })
        
        print(f"[CHART API] Extracted {len(land_features)} land features")
        return jsonify({
            'status': 'ok',
            'features': land_features,
            'count': len(land_features)
        })
    
    except Exception as e:
        print(f"[CHART API] Error loading chart features: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/scene')
def get_scene():
    """Provide consolidated scene data for 3D demo view.
    Returns ship, targets, environment snapshot. Lightweight and read-only.
    """
    try:
        with radar_lock:
            scene = {
                'timestamp': time.time(),
                'ship': {
                    'lat': radar_state['ship'].get('lat', 0.0),
                    'lon': radar_state['ship'].get('lon', 0.0),
                    'heading': radar_state['ship'].get('heading', 0.0),
                    'speed': radar_state['ship'].get('speed', 0.0)
                },
                'targets': [
                    {
                        'id': i,
                        'x': t.get('x', 300),
                        'y': t.get('y', 300),
                        'range': t.get('range', 0.0),
                        'bearing': t.get('bearing', 0.0),
                        'course': t.get('course', 0.0),
                        'speed': t.get('speed', 0.0),
                        'lat': t.get('lat', None),
                        'lon': t.get('lon', None),
                        'vessel_type': t.get('vessel_type', 'power_100plus')
                    }
                    for i, t in enumerate(radar_state.get('targets', []))
                ],
                'env': {
                    'wind_dir': radar_state.get('wind_dir', 0.0),
                    'wind_speed': radar_state.get('wind_speed', 0.0),
                    'mode': radar_state.get('mode', 'NORTH UP'),
                    'motion': radar_state.get('motion', 'RM'),
                    'range_nm': radar_state.get('range_nm', 12.0),
                    'time_of_day': 'day',  # placeholder; can evolve to dynamic later
                }
            }
        return jsonify({'status': 'ok', 'scene': scene})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/land_mesh')
def get_land_mesh():
    """Generate 3D land mesh from LNDARE GeoJSON features.
    Returns triangulated geometry ready for Three.js BufferGeometry.
    Uses simple earcut-style triangulation for polygons.
    """
    try:
        import json
        chart_path = os.path.join(os.path.dirname(__file__), '..', 'chart_export.geojson')
        
        if not os.path.exists(chart_path):
            return jsonify({'status': 'error', 'message': 'Chart file not found'}), 404
        
        # Parse GeoJSON and extract LNDARE features
        with open(chart_path, 'r', encoding='utf-8') as f:
            chart_data = json.load(f)
        
        meshes = []
        
        for feature in chart_data.get('features', []):
            layer = feature.get('properties', {}).get('layer', '')
            if layer != 'LNDARE':
                continue
            
            geom = feature.get('geometry', {})
            geom_type = geom.get('type', '')
            coords = geom.get('coordinates', [])
            
            if geom_type == 'Polygon':
                meshes.extend(_process_polygon_to_mesh(coords))
            elif geom_type == 'MultiPolygon':
                for poly_coords in coords:
                    meshes.extend(_process_polygon_to_mesh(poly_coords))
        
        print(f"[LAND MESH API] Generated {len(meshes)} land mesh segments")
        return jsonify({
            'status': 'ok',
            'meshes': meshes,
            'count': len(meshes)
        })
    
    except Exception as e:
        print(f"[LAND MESH API] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

def _process_polygon_to_mesh(polygon_coords):
    """Convert a polygon to mesh data with earcut-style triangulation.
    polygon_coords: array of rings (first is outer, rest are holes)
    Returns: list of mesh dictionaries with vertices and indices
    """
    if not polygon_coords or len(polygon_coords) == 0:
        return []
    
    # For now, only process outer ring (ignore holes)
    outer_ring = polygon_coords[0]
    if len(outer_ring) < 3:
        return []
    
    # Convert lat/lon to local metric coordinates
    vertices = []
    for lon, lat in outer_ring:
        # Simple equirectangular projection to meters
        # X = meters east, Z = meters north (Three.js convention: -Z is forward/north)
        x = lon * 111320 * math.cos(math.radians(lat))  # meters
        z = -lat * 110540  # meters (negative for Three.js)
        vertices.append({'x': x, 'z': z})
    
    # Simple fan triangulation from first vertex
    # (Works for convex polygons; complex polygons need proper earcut)
    indices = []
    for i in range(1, len(vertices) - 1):
        indices.extend([0, i, i+1])
    
    # Flatten vertices for Three.js
    vertex_array = []
    for v in vertices:
        vertex_array.extend([v['x'], 0, v['z']])  # Y=0 (sea level)
    
    return [{
        'vertices': vertex_array,
        'indices': indices,
        'vertex_count': len(vertices)
    }]

@app.route('/api/set_ship', methods=['POST'])
def set_ship():
    """Update ship geodetic position and motion from external controller/menu.
    Body: { lat, lon, hdg, spd }
    """
    try:
        data = request.get_json(force=True) or {}
        with radar_lock:
            if 'lat' in data:
                radar_state['ship']['lat'] = float(data['lat'])
            if 'lon' in data:
                radar_state['ship']['lon'] = float(data['lon'])
            if 'hdg' in data:
                radar_state['ship']['heading'] = float(data['hdg'])
            if 'spd' in data:
                radar_state['ship']['speed'] = float(data['spd'])
            radar_state['timestamp'] = time.time()
        # Reflect on bridge controls
        with bridge_lock:
            if 'hdg' in data:
                bridge_state['heading'] = float(data['hdg'])
            if 'spd' in data:
                bridge_state['speed'] = float(data['spd'])
            bridge_state['timestamp'] = time.time()

        # Update ECDIS if available
        try:
            from bridge_sim import web_ecdis
            lat = radar_state['ship'].get('lat', 0.0)
            lon = radar_state['ship'].get('lon', 0.0)
            hdg = radar_state['ship'].get('heading', 0.0)
            spd = radar_state['ship'].get('speed', 0.0)
            web_ecdis.update_ship(lat, lon, hdg, spd)
        except Exception:
            pass

        # Notify all UIs
        broadcast_radar_state()
        try:
            broadcast_bridge_state()
        except Exception:
            pass
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"[RADAR API] set_ship error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/init_simulation', methods=['POST'])
def init_simulation():
    """Initialize simulation from web menu scenario"""
    try:
        data = request.get_json()
        print(f"[RADAR API] Initializing simulation with: {data}")
        
        # Initialize radar state with ship data
        with radar_lock:
            # Menu-provided geodetic position
            lat = float(data.get('lat', 0.0))
            lon = float(data.get('lon', 0.0))
            radar_state['ship']['lat'] = lat
            radar_state['ship']['lon'] = lon
            # Heading/speed and environment
            radar_state['ship']['heading'] = float(data.get('hdg', 0))
            radar_state['ship']['speed'] = float(data.get('spd', 0))
            radar_state['wind_dir'] = float(data.get('wind_dir', 0))
            radar_state['wind_speed'] = float(data.get('wind_spd', 0))
            radar_state['timestamp'] = time.time()
            
            # Initialize targets from scenario data
            radar_state['targets'] = []
            
            # Target 1
            t1_rng = float(data.get('t1_rng', 0))
            t1_brg = float(data.get('t1_brg', 0))
            t1_crs = float(data.get('t1_crs', 0))
            t1_spd = float(data.get('t1_spd', 0))
            t1_type = data.get('t1_type', 'power_100plus')  # Get vessel type from scenario
            
            if t1_rng > 0:  # Only create target if range is set
                # Convert polar (range, bearing) to canvas coordinates (x, y) centered at (300,300)
                brg_rad = math.radians(t1_brg)
                range_px = (t1_rng / radar_state['range_nm']) * radar_state['ppi_radius']
                t1_x = 300 + range_px * math.sin(brg_rad)
                t1_y = 300 - range_px * math.cos(brg_rad)
                
                # Calculate lat/lon from ship position + range/bearing for 3D bridge view
                ship_lat = radar_state['ship'].get('lat', 0.0)
                ship_lon = radar_state['ship'].get('lon', 0.0)
                # Bearing is TRUE bearing (from north), convert to radians
                # Convert nautical miles to meters (1 NM = 1852 m)
                range_m = t1_rng * 1852.0
                # Calculate offset in lat/lon using standard navigation formulas
                # 1 degree latitude ≈ 111,320 meters
                # 1 degree longitude ≈ 111,320 * cos(latitude) meters
                lat_m_per_deg = 111320.0
                lon_m_per_deg = 111320.0 * math.cos(math.radians(ship_lat))
                # Bearing: 0° = North, 90° = East
                # dLat = range * cos(bearing) - northward component
                # dLon = range * sin(bearing) - eastward component
                dlat = (range_m * math.cos(brg_rad)) / lat_m_per_deg
                dlon = (range_m * math.sin(brg_rad)) / lon_m_per_deg
                t1_lat = ship_lat + dlat
                t1_lon = ship_lon + dlon
                
                print(f"[RADAR API]   Ship: lat={ship_lat:.6f}, lon={ship_lon:.6f}")
                print(f"[RADAR API]   Target 1 brg={t1_brg}°, rng={t1_rng} NM")
                print(f"[RADAR API]   Target 1 offset: dlat={dlat:.6f}, dlon={dlon:.6f}")
                print(f"[RADAR API]   Target 1: lat={t1_lat:.6f}, lon={t1_lon:.6f}")

                radar_state['targets'].append({
                    'id': 1,
                    'x': t1_x,
                    'y': t1_y,
                    'lat': t1_lat,
                    'lon': t1_lon,
                    'course': t1_crs,
                    'speed': t1_spd,
                    'range': t1_rng,
                    'bearing': t1_brg,
                    'vessel_type': t1_type
                })
                print(f"[RADAR API] ✓ Target 1 created: RNG={t1_rng} NM, BRG={t1_brg}°, CRS={t1_crs}°, SPD={t1_spd} kn, TYPE={t1_type}")
            
            # Target 2
            t2_rng = float(data.get('t2_rng', 0))
            t2_brg = float(data.get('t2_brg', 0))
            t2_crs = float(data.get('t2_crs', 0))
            t2_spd = float(data.get('t2_spd', 0))
            t2_type = data.get('t2_type', 'power_100plus')  # Get vessel type from scenario
            
            if t2_rng > 0:  # Only create target if range is set
                # Convert polar (range, bearing) to canvas coordinates (x, y) centered at (300,300)
                brg_rad = math.radians(t2_brg)
                range_px = (t2_rng / radar_state['range_nm']) * radar_state['ppi_radius']
                t2_x = 300 + range_px * math.sin(brg_rad)
                t2_y = 300 - range_px * math.cos(brg_rad)
                
                # Calculate lat/lon from ship position + range/bearing for 3D bridge view
                ship_lat = radar_state['ship'].get('lat', 0.0)
                ship_lon = radar_state['ship'].get('lon', 0.0)
                # Bearing is TRUE bearing (from north), convert to radians
                # Convert nautical miles to meters (1 NM = 1852 m)
                range_m = t2_rng * 1852.0
                # Calculate offset in lat/lon using standard navigation formulas
                lat_m_per_deg = 111320.0
                lon_m_per_deg = 111320.0 * math.cos(math.radians(ship_lat))
                # Bearing: 0° = North, 90° = East
                dlat = (range_m * math.cos(brg_rad)) / lat_m_per_deg
                dlon = (range_m * math.sin(brg_rad)) / lon_m_per_deg
                t2_lat = ship_lat + dlat
                t2_lon = ship_lon + dlon
                
                print(f"[RADAR API]   Target 2 brg={t2_brg}°, rng={t2_rng} NM")
                print(f"[RADAR API]   Target 2 offset: dlat={dlat:.6f}, dlon={dlon:.6f}")
                print(f"[RADAR API]   Target 2: lat={t2_lat:.6f}, lon={t2_lon:.6f}")

                radar_state['targets'].append({
                    'id': 2,
                    'x': t2_x,
                    'y': t2_y,
                    'lat': t2_lat,
                    'lon': t2_lon,
                    'course': t2_crs,
                    'speed': t2_spd,
                    'range': t2_rng,
                    'bearing': t2_brg,
                    'vessel_type': t2_type
                })
                print(f"[RADAR API] ✓ Target 2 created: RNG={t2_rng} NM, BRG={t2_brg}°, CRS={t2_crs}°, SPD={t2_spd} kn, TYPE={t2_type}")
            
        # Initialize bridge controls
        with bridge_lock:
            bridge_state['heading'] = float(data.get('hdg', 0))
            bridge_state['speed'] = float(data.get('spd', 0))
            bridge_state['timestamp'] = time.time()

        print(f"[RADAR API] ✓ Ship state initialized: LAT={radar_state['ship']['lat']}, LON={radar_state['ship']['lon']}, HDG={radar_state['ship']['heading']}°, SPD={radar_state['ship']['speed']} kn")

        # Initialize ECDIS ship state
        try:
            from bridge_sim import web_ecdis
            lat_ec = float(data.get('lat', radar_state['ship']['lat']))
            lon_ec = float(data.get('lon', radar_state['ship']['lon']))
            hdg_ec = float(data.get('hdg', radar_state['ship']['heading']))
            spd_ec = float(data.get('spd', radar_state['ship']['speed']))
            web_ecdis.update_ship(lat_ec, lon_ec, hdg_ec, spd_ec)
            print(f"[RADAR API] ✓ ECDIS initialized: LAT={lat_ec}, LON={lon_ec}")
        except Exception as e:
            print(f"[RADAR API] ECDIS init warning: {e}")
        # Push initial state to connected clients
        try:
            broadcast_radar_state()
        except Exception:
            pass
        try:
            broadcast_bridge_state()
        except Exception:
            pass
        
        # Ensure background integrator is running
        _start_background_integrator()

        return jsonify({'status': 'ok', 'message': 'Simulation initialized'})
    except Exception as e:
        print(f"[RADAR API] Init error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@sock.route('/radar')
def radar_websocket(ws):
    """WebSocket endpoint for live radar updates"""
    print(f"[RADAR WS] New connection attempt...")
    radar_ws_clients.append(ws)
    print(f"[RADAR WS] Client connected (total: {len(radar_ws_clients)})")
    
    try:
        # Send initial state
        with radar_lock:
            initial_state = json.dumps(radar_state)
            print(f"[RADAR WS] Sending initial state: heading={radar_state['ship']['heading']}, speed={radar_state['ship']['speed']}")
            ws.send(initial_state)
        
        # Handle client commands
        while True:
            try:
                data = ws.receive(timeout=1.0)
                if data:
                    cmd = json.loads(data)
                    print(f"[RADAR WS] Received command: {cmd}")
                    handle_radar_command(cmd)
            except TimeoutError:
                # Timeout is normal, just continue
                pass
            except Exception as e:
                # Other errors might indicate disconnection
                print(f"[RADAR WS] Receive error: {e}")
                break
            time.sleep(0.01)
    except Exception as e:
        print(f"[RADAR WS] Connection error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if ws in radar_ws_clients:
            radar_ws_clients.remove(ws)
        print(f"[RADAR WS] Client disconnected (total: {len(radar_ws_clients)})")

def _recalculate_target_positions():
    """Recalculate target x/y positions from range/bearing based on current radar range.
    Must be called with radar_lock held."""
    print(f"[RADAR] Recalculating target positions for range {radar_state['range_nm']} NM")
    for target in radar_state['targets']:
        if 'range' in target and 'bearing' in target:
            # Convert range/bearing to canvas coordinates
            brg_rad = math.radians(target['bearing'])
            range_px = (target['range'] / radar_state['range_nm']) * radar_state['ppi_radius']
            old_x, old_y = target.get('x', 0), target.get('y', 0)
            target['x'] = 300 + range_px * math.sin(brg_rad)
            target['y'] = 300 - range_px * math.cos(brg_rad)
            print(f"[RADAR] Target {target.get('id', '?')}: RNG={target['range']:.2f} NM, BRG={target['bearing']:.1f}° → X={old_x:.1f}→{target['x']:.1f}, Y={old_y:.1f}→{target['y']:.1f}")


def handle_radar_command(cmd):
    """Process commands from the web radar UI"""
    command = cmd.get('command')
    value = cmd.get('value')
    
    with radar_lock:
        if command == 'range_inc':
            old_range = radar_state['range_nm']
            try:
                i = RANGES.index(radar_state['range_nm'])
                if i < len(RANGES) - 1:
                    radar_state['range_nm'] = RANGES[i + 1]
                    print(f"[RADAR CMD] Range increased: {old_range} → {radar_state['range_nm']} NM")
                    # Recalculate target positions for new range
                    _recalculate_target_positions()
            except ValueError:
                bigger = [r for r in RANGES if r > radar_state['range_nm']]
                if bigger:
                    radar_state['range_nm'] = bigger[0]
                    print(f"[RADAR CMD] Range increased: {old_range} → {radar_state['range_nm']} NM")
                    _recalculate_target_positions()
        
        elif command == 'range_dec':
            old_range = radar_state['range_nm']
            try:
                i = RANGES.index(radar_state['range_nm'])
                if i > 0:
                    radar_state['range_nm'] = RANGES[i - 1]
                    print(f"[RADAR CMD] Range decreased: {old_range} → {radar_state['range_nm']} NM")
                    # Recalculate target positions for new range
                    _recalculate_target_positions()
            except ValueError:
                smaller = [r for r in RANGES if r < radar_state['range_nm']]
                if smaller:
                    radar_state['range_nm'] = smaller[-1]
                    print(f"[RADAR CMD] Range decreased: {old_range} → {radar_state['range_nm']} NM")
                    _recalculate_target_positions()
        
        elif command == 'toggle_mode':
            if radar_state['north_up']:
                radar_state['north_up'] = False
                radar_state['mode'] = 'COURSE UP'
                radar_state['fixed_heading'] = radar_state['ship']['heading']
            else:
                radar_state['north_up'] = True
                radar_state['mode'] = 'NORTH UP'
        
        elif command == 'toggle_motion':
            prev_motion = radar_state['motion']
            radar_state['motion'] = 'TM' if radar_state['motion'] == 'RM' else 'RM'
            # Reset ship to center when switching to RM
            if prev_motion == 'TM' and radar_state['motion'] == 'RM':
                radar_state['ship']['x'] = 300
                radar_state['ship']['y'] = 300
        
        elif command == 'toggle_rings':
            radar_state['range_rings'] = not radar_state['range_rings']
        
        elif command == 'toggle_tx':
            radar_state['tx_on'] = not radar_state['tx_on']
        
        elif command == 'toggle_ebl':
            radar_state['ebl_visible'] = not radar_state['ebl_visible']
        
        elif command == 'toggle_vrm':
            radar_state['vrm_visible'] = not radar_state['vrm_visible']
        
        elif command == 'set_ebl':
            radar_state['ebl_bearing'] = float(value) % 360
        
        elif command == 'set_vrm':
            radar_state['vrm_radius'] = max(0.5, min(radar_state['range_nm'], float(value)))
        
        elif command == 'set_gain':
            radar_state['gain'] = int(value)
        
        elif command == 'set_sea':
            radar_state['sea'] = int(value)
        
        elif command == 'set_rain':
            radar_state['rain'] = int(value)
        
        elif command == 'center_ship':
            # Center ship at PPI center
            radar_state['ship']['x'] = 300
            radar_state['ship']['y'] = 300
        
        elif command == 'offset':
            # Offset logic would be implemented here
            pass
        
        elif command == 'center':
            # Center logic would be implemented here
            pass
    
    # Broadcast updated state
    broadcast_radar_state()

def update_radar_data(ship_x, ship_y, heading, speed, targets=None, clutter=None):
    """
    Update radar data and broadcast to all connected clients.
    
    Called by the simulator to push updates.
    """
    with radar_lock:
        radar_state['ship']['x'] = ship_x
        radar_state['ship']['y'] = ship_y
        radar_state['ship']['heading'] = heading
        radar_state['ship']['speed'] = speed
        
        if targets is not None:
            radar_state['targets'] = targets
        
        if clutter is not None:
            radar_state['clutter'] = clutter
        
        radar_state['timestamp'] = time.time()
        
        # Debug: log updates occasionally
        if not hasattr(update_radar_data, '_counter'):
            update_radar_data._counter = 0
        update_radar_data._counter += 1
        if update_radar_data._counter % 60 == 0:
            print(f"[RADAR SERVER] State updated: heading={heading}°, speed={speed} kn, clients={len(radar_ws_clients)}")
    
    broadcast_radar_state()

def broadcast_radar_state():
    """Send current radar state to all connected clients"""
    with radar_lock:
        message = json.dumps(radar_state)
    
    disconnected = []
    for ws in radar_ws_clients:
        try:
            ws.send(message)
        except Exception:
            disconnected.append(ws)
    
    # Clean up disconnected clients
    for ws in disconnected:
        if ws in radar_ws_clients:
            radar_ws_clients.remove(ws)

# ---------------- Background integrator for dead-reckoning and target motion -----------------
_bg_thread = None
_bg_running = False

def _background_integrator():
    global _bg_running
    prev = time.time()
    # Simple clutter regeneration timer
    clutter_timer = 0.0
    print("[BG INTEGRATOR] ✓ Starting dead-reckoning loop...")
    iteration = 0
    while _bg_running:
        now = time.time()
        dt = max(0.0, min(1.0, now - prev))  # clamp dt to avoid spikes
        prev = now
        iteration += 1

        # Dead reckon own ship geodetic position if speed > 0
        try:
            with radar_lock:
                hdg = float(radar_state['ship'].get('heading', 0.0))
                spd = float(radar_state['ship'].get('speed', 0.0))
                lat = float(radar_state['ship'].get('lat', 0.0))
                lon = float(radar_state['ship'].get('lon', 0.0))
            
            # Debug log state even if not moving
            if iteration % 25 == 0:
                print(f"[BG INTEGRATOR] State: LAT={lat:.5f}, LON={lon:.5f}, HDG={hdg:.1f}°, SPD={spd:.1f} kn")
            
            if spd > 0.0:
                d_nm = spd * (dt / 3600.0)
                north_nm = d_nm * math.cos(math.radians(hdg))
                east_nm = d_nm * math.sin(math.radians(hdg))
                lat += north_nm / 60.0
                # Prevent division by zero at poles
                lon += east_nm / (60.0 * max(0.0001, math.cos(math.radians(lat))))
                
                # Update canvas coordinates depending on motion mode
                with radar_lock:
                    rng_nm = float(radar_state.get('range_nm', 12.0)) or 12.0
                    ppi = float(radar_state.get('ppi_radius', 250)) or 250.0
                    north_up = bool(radar_state.get('north_up', True))
                    fixed_heading = float(radar_state.get('fixed_heading', 0.0))
                    motion = str(radar_state.get('motion', 'RM'))
                    px_per_nm = ppi / rng_nm

                    if motion == 'TM':
                        # Calculate pixel movement (True Motion: ship moves on screen)
                        px_per_sec = (spd * px_per_nm) / 3600.0
                        display_hdg = hdg if north_up else (hdg - fixed_heading)
                        ang = math.radians(display_hdg)
                        dx = px_per_sec * dt * math.sin(ang)
                        dy = -px_per_sec * dt * math.cos(ang)

                        x = radar_state['ship']['x'] + dx
                        y = radar_state['ship']['y'] + dy

                        # Auto-recenter when ship gets too far from center (> 80% of radius)
                        dist_from_center = math.sqrt((x - 300)**2 + (y - 300)**2)
                        if dist_from_center > ppi * 0.8:
                            x = 300
                            y = 300
                    else:
                        # Relative Motion: ship remains at center; land/targets move relative
                        x = 300
                        y = 300

                    radar_state['ship']['x'] = x
                    radar_state['ship']['y'] = y
                    radar_state['ship']['lat'] = lat
                    radar_state['ship']['lon'] = lon
                    radar_state['timestamp'] = now
                    
                    # Debug log every 25 iterations (~5 sec)
                    if iteration % 25 == 0:
                        print(f"[BG INTEGRATOR] DR update: LAT={lat:.5f}, LON={lon:.5f}, X={x:.1f}, Y={y:.1f}, HDG={hdg:.1f}°, SPD={spd:.1f} kn")
                
                # Push to ECDIS
                try:
                    from bridge_sim import web_ecdis
                    web_ecdis.update_ship(lat, lon, hdg, spd)
                except Exception as e:
                    if iteration % 25 == 0:
                        print(f"[BG INTEGRATOR] ECDIS update failed: {e}")
        except Exception as e:
            if iteration % 25 == 0:
                print(f"[BG INTEGRATOR] DR error: {e}")

        # Move radar targets by their course/speed in screen space
        try:
            with radar_lock:
                rng_nm = float(radar_state.get('range_nm', 12.0)) or 12.0
                ppi = float(radar_state.get('ppi_radius', 250)) or 250.0
                north_up = bool(radar_state.get('north_up', True))
                fixed_heading = float(radar_state.get('fixed_heading', 0.0))
                targets = radar_state['targets']
                px_per_nm = ppi / rng_nm
            if targets:
                cos_cache = {}
                for t in targets:
                    try:
                        spd = float(t.get('speed', 0.0))
                        crs = float(t.get('course', 0.0))
                        if spd <= 0.0:
                            continue
                        px_per_sec = (spd * px_per_nm) / 3600.0
                        # Account for display rotation if COURSE UP
                        display_brg = crs if north_up else (crs - fixed_heading)
                        ang = math.radians(display_brg)
                        dx = px_per_sec * dt * math.sin(ang)
                        dy = -px_per_sec * dt * math.cos(ang)
                        t['x'] = (t.get('x', 300)) + dx
                        t['y'] = (t.get('y', 300)) + dy
                        
                        # Also update range/bearing from new x/y position
                        rel_x = t['x'] - 300
                        rel_y = t['y'] - 300
                        range_px = math.sqrt(rel_x**2 + rel_y**2)
                        t['range'] = (range_px / ppi) * rng_nm
                        # Calculate bearing (0° = North, clockwise)
                        brg_rad = math.atan2(rel_x, -rel_y)
                        t['bearing'] = (math.degrees(brg_rad) + 360) % 360
                    except Exception:
                        continue
                with radar_lock:
                    radar_state['timestamp'] = now
        except Exception:
            pass

        # Occasionally broadcast to clients (5 Hz)
        try:
            broadcast_radar_state()
        except Exception:
            pass

        time.sleep(0.2)

def _start_background_integrator():
    global _bg_thread, _bg_running
    if _bg_thread and _bg_thread.is_alive():
        print("[BG INTEGRATOR] Already running")
        return
    print("[BG INTEGRATOR] Starting background thread...")
    _bg_running = True
    _bg_thread = threading.Thread(target=_background_integrator, daemon=True)
    _bg_thread.start()
    print("[BG INTEGRATOR] Background thread started")

def run_radar_server(host='127.0.0.1', port=5001, debug=False):
    """
    Start the Flask radar server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    print(f"[RADAR WEB] Starting radar web server on http://{host}:{port}/radar")
    print(f"[RADAR WEB] Open http://{host}:{port}/radar in your browser")
    # Start background integrator for ship DR and moving targets
    _start_background_integrator()
    app.run(host=host, port=port, debug=debug, use_reloader=False)

if __name__ == '__main__':
    # Standalone test mode with demo data
    def demo_radar():
        """Simulate radar data for testing"""
        angle = 0
        # Initial positions for moving targets
        target1_lat = 0.0  # Relative position in NM
        target1_lon = 0.0
        target2_lat = 0.0
        target2_lon = 0.0
        
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            # Ship heading (slowly changing)
            heading = (angle * 0.5) % 360
            
            # Generate sea clutter (reduced, more realistic)
            clutter = []
            for _ in range(150):
                r = random.uniform(30, 180)
                theta = random.uniform(0, 360)
                x = 300 + r * math.sin(math.radians(theta))
                y = 300 - r * math.cos(math.radians(theta))
                # Only show clutter in certain sectors (weather)
                if 30 < theta < 150 or 200 < theta < 280:
                    clutter.append({'x': int(x), 'y': int(y)})
            
            # TARGETS THAT ACTUALLY MOVE based on their course and speed
            # Target 1: Moving at course 230° at 18 knots
            target1_course = 230
            target1_speed = 18.0
            # Update position (NM traveled = speed * time_hours)
            time_hours = elapsed / 3600.0
            target1_lat = 3.5 + target1_speed * time_hours * math.cos(math.radians(target1_course))
            target1_lon = 3.5 + target1_speed * time_hours * math.sin(math.radians(target1_course))
            
            # Convert to range/bearing
            target1_range_nm = math.sqrt(target1_lat**2 + target1_lon**2)
            target1_bearing = (math.degrees(math.atan2(target1_lon, target1_lat)) + 360) % 360
            
            # Target 2: Moving at course 090° at 12 knots
            target2_course = 90
            target2_speed = 12.0
            target2_lat = -3.0 + target2_speed * time_hours * math.cos(math.radians(target2_course))
            target2_lon = 0.5 + target2_speed * time_hours * math.sin(math.radians(target2_course))
            
            # Convert to range/bearing
            target2_range_nm = math.sqrt(target2_lat**2 + target2_lon**2)
            target2_bearing = (math.degrees(math.atan2(target2_lon, target2_lat)) + 360) % 360
            
            # Convert range/bearing to pixels for display
            # Using the radar's range_nm and ppi_radius to convert
            current_range_nm = radar_state['range_nm']
            ppi_radius = radar_state['ppi_radius']
            
            # Target 1 position in pixels
            t1_range_px = (target1_range_nm / current_range_nm) * ppi_radius
            t1_x = 300 + t1_range_px * math.sin(math.radians(target1_bearing))
            t1_y = 300 - t1_range_px * math.cos(math.radians(target1_bearing))
            
            # Target 2 position in pixels
            t2_range_px = (target2_range_nm / current_range_nm) * ppi_radius
            t2_x = 300 + t2_range_px * math.sin(math.radians(target2_bearing))
            t2_y = 300 - t2_range_px * math.cos(math.radians(target2_bearing))
            
            targets = [
                {
                    'x': t1_x,
                    'y': t1_y,
                    'bearing': target1_bearing,
                    'range_nm': target1_range_nm,
                    'course': target1_course,
                    'speed': target1_speed
                },
                {
                    'x': t2_x,
                    'y': t2_y,
                    'bearing': target2_bearing,
                    'range_nm': target2_range_nm,
                    'course': target2_course,
                    'speed': target2_speed
                }
            ]
            
            # Debug print every 50 updates
            if angle % 50 == 0:
                print(f"[DEBUG] Time: {elapsed:.1f}s, Generated 2 targets:")
                print(f"  T1: {target1_range_nm:.2f}NM @ {target1_bearing:.0f}° CRS:{target1_course}° SPD:{target1_speed}kn")
                print(f"  T2: {target2_range_nm:.2f}NM @ {target2_bearing:.0f}° CRS:{target2_course}° SPD:{target2_speed}kn")
            
            # Always send targets even if TX is off; client will draw them independently
            update_radar_data(300, 300, heading, 15.0, targets, clutter if radar_state['tx_on'] else [])
            
            angle += 1
            time.sleep(0.2)
    
    # Start demo in background
    demo_thread = threading.Thread(target=demo_radar, daemon=True)
    demo_thread.start()
    
    # Run server
    run_radar_server(debug=False)

# ========== BRIDGE CONTROLS ENDPOINTS ==========

@app.route('/bridge_controls')
def bridge_controls_index():
    """Serve the bridge controls HTML"""
    web_dir = os.path.dirname(__file__)
    return send_from_directory(web_dir, 'bridge_controls.html')

@app.route('/api/bridge')
def get_bridge():
    """REST endpoint for current bridge state"""
    with bridge_lock:
        return jsonify(bridge_state)

@sock.route('/bridge')
def bridge_websocket(ws):
    """WebSocket endpoint for live bridge updates"""
    print(f"[BRIDGE WS] New connection attempt...")
    bridge_ws_clients.append(ws)
    print(f"[BRIDGE WS] Client connected (total: {len(bridge_ws_clients)})")
    
    try:
        # Send initial state
        with bridge_lock:
            initial_state = {'type': 'bridge_state', **bridge_state}
            ws.send(json.dumps(initial_state))
        
        # Handle client commands
        while True:
            try:
                data = ws.receive(timeout=1.0)
                if data:
                    handle_bridge_command(json.loads(data))
            except TimeoutError:
                pass
            except Exception as e:
                print(f"[BRIDGE WS] Error receiving: {e}")
                break
    except Exception as e:
        print(f"[BRIDGE WS] Client error: {e}")
    finally:
        if ws in bridge_ws_clients:
            bridge_ws_clients.remove(ws)
        print(f"[BRIDGE WS] Client disconnected (remaining: {len(bridge_ws_clients)})")

def handle_bridge_command(cmd):
    """Handle commands from bridge controls client"""
    command = cmd.get('command')
    value = cmd.get('value')
    
    print(f"[BRIDGE CMD] {command} = {value}")
    
    with bridge_lock:
        if command == 'set_rudder':
            bridge_state['rudder_angle'] = max(-35, min(35, float(value)))
        elif command == 'set_telegraph':
            bridge_state['telegraph'] = value
            # Update RPM based on telegraph
            rpm_map = {
                'FULL_ASTERN': -120,
                'HALF_ASTERN': -80,
                'SLOW_ASTERN': -40,
                'STOP': 0,
                'SLOW_AHEAD': 40,
                'HALF_AHEAD': 80,
                'FULL_AHEAD': 120
            }
            bridge_state['rpm'] = rpm_map.get(value, 0)
        elif command == 'motor1':
            bridge_state['motor1'] = value
        elif command == 'motor2':
            bridge_state['motor2'] = value
        
        bridge_state['timestamp'] = time.time()
    
    # Broadcast to all connected bridge clients
    broadcast_bridge_state()

def update_bridge_data(heading, speed, rpm, rot, rudder_angle):
    """Update bridge state from simulator"""
    with bridge_lock:
        bridge_state['heading'] = heading
        bridge_state['speed'] = speed
        bridge_state['rpm'] = rpm
        bridge_state['rot'] = rot
        bridge_state['rudder_angle'] = rudder_angle
        bridge_state['timestamp'] = time.time()
    
    broadcast_bridge_state()

def broadcast_bridge_state():
    """Send current bridge state to all connected WebSocket clients"""
    if not bridge_ws_clients:
        return
    
    with bridge_lock:
        msg = json.dumps({'type': 'bridge_state', **bridge_state})
    
    # Send to all clients (remove dead ones)
    dead_clients = []
    for client in bridge_ws_clients:
        try:
            client.send(msg)
        except Exception as e:
            print(f"[BRIDGE WS] Failed to send to client: {e}")
            dead_clients.append(client)
    
    for client in dead_clients:
        if client in bridge_ws_clients:
            bridge_ws_clients.remove(client)

