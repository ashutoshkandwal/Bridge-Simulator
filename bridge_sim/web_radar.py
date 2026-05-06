"""Bridge helpers for the Flask/canvas radar web server."""

from __future__ import annotations

import threading
import webbrowser

_server_started = False
_server_thread = None


def start_web_radar(host='127.0.0.1', port=5001, open_browser=False):
    """Start web.radar_server in a background thread if it is not already running."""
    global _server_started, _server_thread
    if _server_started:
        return True
    try:
        from web import radar_server
    except Exception as exc:
        print(f"[WEB RADAR] Import failed: {exc}")
        return False

    def _run():
        radar_server.run_server(host=host, port=port, debug=False)

    _server_thread = threading.Thread(target=_run, daemon=True)
    _server_thread.start()
    _server_started = True
    if open_browser:
        try:
            webbrowser.open(f"http://{host}:{port}/")
        except Exception:
            pass
    return True


def is_web_radar_running():
    return _server_started


def push_radar_update(ship_x, ship_y, heading, speed, targets=None, clutter=None):
    """Push radar data into web.radar_server state and broadcast when available."""
    try:
        from web import radar_server
        with radar_server.radar_lock:
            radar_server.radar_state['ship']['x'] = float(ship_x)
            radar_server.radar_state['ship']['y'] = float(ship_y)
            radar_server.radar_state['ship']['heading'] = float(heading)
            radar_server.radar_state['ship']['speed'] = float(speed)
            if targets is not None:
                radar_server.radar_state['targets'] = targets
            if clutter is not None:
                radar_server.radar_state['clutter'] = clutter
            radar_server.radar_state['timestamp'] = __import__('time').time()
        radar_server.broadcast_radar_state()
    except Exception as exc:
        print(f"[WEB RADAR] push_radar_update failed: {exc}")
