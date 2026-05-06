"""Bridge helpers for the Flask/Leaflet ECDIS web server."""

from __future__ import annotations

import threading
import webbrowser

_server_started = False
_server_thread = None


def start_web_ecdis(host='127.0.0.1', port=5000, open_browser=False):
    """Start web.server in a background thread if it is not already running."""
    global _server_started, _server_thread
    if _server_started:
        return True
    try:
        from web import server as ecdis_server
    except Exception as exc:
        print(f"[WEB ECDIS] Import failed: {exc}")
        return False

    def _run():
        ecdis_server.run_server(host=host, port=port, debug=False)

    _server_thread = threading.Thread(target=_run, daemon=True)
    _server_thread.start()
    _server_started = True
    if open_browser:
        try:
            webbrowser.open(f"http://{host}:{port}/")
        except Exception:
            pass
    return True


def update_ship(lat, lon, heading, speed):
    """Push own-ship data to the web ECDIS server state."""
    try:
        from web import server as ecdis_server
        ecdis_server.update_ship_position(float(lat), float(lon), float(heading), float(speed))
    except Exception as exc:
        print(f"[WEB ECDIS] update_ship failed: {exc}")
