"""Bridge Simulator entrypoint.

Current project focus:
- radar display
- bridge/control panel
- visual window placeholder
- NMEA output to real MARIS ECDIS900 over LAN

Internal ECDIS/chart loading is intentionally disabled in this entrypoint. The
real MARIS ECDIS is now the chart display and receives own-ship data through
bridge_sim.nmea_sender.
"""

from __future__ import annotations

import math
import time
import threading

import pygame as pg
from pygame import RESIZABLE

from bridge_sim.controls import Controls
from bridge_sim.models import Ship
from bridge_sim.nmea_sender import NMEASender
from bridge_sim.radar import RadarDisplay
from bridge_sim.utils import load_config, load_last_scenario, save_last_scenario


class App:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.cfg = load_config()
        self.nmea = NMEASender.from_dict(self.cfg.get("nmea_output", {}))

        self.ship_lat = 49.500000
        self.ship_lon = -6.000000
        self.ship_heading = 80.0
        self.ship_speed = 12.0
        self.wind_dir = 0.0
        self.wind_speed = 0.0

        last = load_last_scenario() or {}
        self.ship_lat = float(last.get("lat", self.ship_lat))
        self.ship_lon = float(last.get("lon", self.ship_lon))
        self.ship_heading = float(last.get("hdg", self.ship_heading))
        self.ship_speed = float(last.get("spd", self.ship_speed))
        self.wind_dir = float(last.get("wind_dir", self.wind_dir))
        self.wind_speed = float(last.get("wind_spd", self.wind_speed))

        self.ship = Ship(320, 310, self.ship_heading, self.ship_speed, self.ship_lat, self.ship_lon)
        self.state = "menu"
        self.controls = None
        self.radar = None
        self.clock = None
        self.screen = None

        self.target_specs = []
        self.sim_time_scale = 1.0
        self._last_nmea_log = 0.0
        self._running = True

        self._start_web_servers()

        if not self.headless:
            pg.init()
            self.clock = pg.time.Clock()
            self.screen = pg.display.set_mode((1100, 618), RESIZABLE)
            pg.display.set_caption("BRIDGE SIMULATOR")
            self.controls = Controls()
            self.radar = RadarDisplay(self.screen, cfg=self.cfg, ship=self.ship)
            self.font_big = pg.font.SysFont(None, 48)
            self.font = pg.font.SysFont(None, 26)
            self.font_small = pg.font.SysFont(None, 20)
            self._setup_menu_fields()
        else:
            self._start_headless_loop()

    def _start_web_servers(self) -> None:
        try:
            from bridge_sim import web_radar
            web_radar.start_web_radar(host="0.0.0.0", port=5001, open_browser=False)
            print("[MAIN] Web radar/menu started on port 5001")
        except Exception as exc:
            print(f"[MAIN] Web radar start failed: {exc}")

    def _start_headless_loop(self) -> None:
        thread = threading.Thread(target=self._headless_loop, daemon=True)
        thread.start()

    def _headless_loop(self) -> None:
        """In Codespaces/headless mode, keep NMEA aligned with web radar state."""
        print("[MAIN] Headless mode active. Open forwarded port 5001 for the web menu/radar.")
        last_time = time.time()
        while self._running:
            now = time.time()
            dt = now - last_time
            last_time = now
            self._sync_from_web_state()
            self.ship.update_position(dt, north=0)
            self._push_state_to_web()
            self._send_nmea()
            time.sleep(0.05)

    def _sync_from_web_state(self) -> None:
        """Read ship values from the web radar server if available."""
        try:
            from web.radar_server import radar_lock, radar_state
            with radar_lock:
                ship_data = radar_state.get("ship", {})
                self.ship.lat = float(ship_data.get("lat", self.ship.lat))
                self.ship.lon = float(ship_data.get("lon", self.ship.lon))
                self.ship.heading = float(ship_data.get("heading", self.ship.heading))
                self.ship.speed = float(ship_data.get("speed", self.ship.speed))
        except Exception:
            pass

    def _push_state_to_web(self) -> None:
        try:
            from bridge_sim import web_radar
            web_radar.push_radar_update(
                300,
                300,
                self.ship.heading,
                self.ship.speed,
                targets=[],
                clutter=[],
            )
        except Exception:
            pass

        try:
            from web.radar_server import update_bridge_data
            rpm = int(self.ship.speed * 8)
            update_bridge_data(self.ship.heading, self.ship.speed, rpm, 0.0, 0.0)
        except Exception:
            pass

    def _send_nmea(self) -> None:
        sent = self.nmea.send_ship(
            lat=self.ship.lat,
            lon=self.ship.lon,
            heading=self.ship.heading,
            speed_kn=self.ship.speed,
            cog=self.ship.heading,
        )
        if sent and time.time() - self._last_nmea_log > 10.0:
            print(
                f"[NMEA] Sent own ship to {self.nmea.config.host}:{self.nmea.config.port} "
                f"LAT={self.ship.lat:.6f} LON={self.ship.lon:.6f} "
                f"HDG={self.ship.heading:.1f} SPD={self.ship.speed:.1f}"
            )
            self._last_nmea_log = time.time()

    def _setup_menu_fields(self) -> None:
        def field(value, x, y):
            return {"value": str(value), "active": False, "rect": pg.Rect(x, y, 150, 30)}

        self.input_fields = {
            "lat": field(self.ship.lat, 250, 120),
            "lon": field(self.ship.lon, 250, 160),
            "hdg": field(self.ship.heading, 250, 200),
            "spd": field(self.ship.speed, 250, 240),
            "wind_dir": field(self.wind_dir, 250, 300),
            "wind_spd": field(self.wind_speed, 250, 340),
        }

    def run(self) -> None:
        if self.headless:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("[MAIN] Shutting down")
                self._running = False
            return

        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    running = False

            if self.state == "menu":
                self._handle_menu_input(events)
                self._draw_menu()
            else:
                self.controls.handle(self, dt, events)
                self.ship.update_position(dt, north=0)
                self._push_state_to_web()
                self._send_nmea()

                if self.state == "radar":
                    self.radar.update(dt, events)
                    self.radar.draw()
                elif self.state == "controls":
                    self._draw_controls()
                elif self.state == "visual":
                    self._draw_visual()

            pg.display.flip()

        self._running = False
        self.nmea.close()
        pg.quit()

    def _cycle_state(self) -> None:
        order = ["menu", "radar", "controls", "visual"]
        current = order.index(self.state)
        self.state = order[(current + 1) % len(order)]
        pg.display.set_caption(self.state.upper())
        if self.state == "radar" and self.radar:
            self.radar.on_show()
        elif self.radar:
            self.radar.on_hide()

    def _handle_menu_input(self, events) -> None:
        field_order = ["lat", "lon", "hdg", "spd", "wind_dir", "wind_spd"]
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                for field_name, field_data in self.input_fields.items():
                    field_data["active"] = field_data["rect"].collidepoint(event.pos)

            if event.type == pg.KEYDOWN:
                active_field = next((name for name, data in self.input_fields.items() if data["active"]), None)
                if active_field:
                    if event.key == pg.K_BACKSPACE:
                        self.input_fields[active_field]["value"] = self.input_fields[active_field]["value"][:-1]
                    elif event.key == pg.K_RETURN:
                        idx = field_order.index(active_field)
                        self.input_fields[active_field]["active"] = False
                        if idx < len(field_order) - 1:
                            self.input_fields[field_order[idx + 1]]["active"] = True
                    elif event.unicode.isdigit() or event.unicode in ".-":
                        self.input_fields[active_field]["value"] += event.unicode

                if event.key == pg.K_SPACE:
                    self._apply_menu_values()
                    self._cycle_state()

    def _apply_menu_values(self) -> None:
        try:
            self.ship.lat = float(self.input_fields["lat"]["value"])
            self.ship.lon = float(self.input_fields["lon"]["value"])
            self.ship.heading = float(self.input_fields["hdg"]["value"]) % 360.0
            self.ship.speed = max(0.0, float(self.input_fields["spd"]["value"]))
            self.wind_dir = float(self.input_fields["wind_dir"]["value"]) % 360.0
            self.wind_speed = max(0.0, float(self.input_fields["wind_spd"]["value"]))
            save_last_scenario({name: data["value"] for name, data in self.input_fields.items()})
        except ValueError:
            print("[MAIN] Invalid menu value ignored")

    def _draw_menu(self) -> None:
        self.screen.fill((0, 0, 80))
        self.screen.blit(self.font_big.render("BRIDGE SIMULATOR SETUP", True, (255, 255, 255)), (40, 30))
        self.screen.blit(self.font.render("Own Ship", True, (180, 255, 180)), (40, 85))

        labels = [
            ("Latitude:", "lat"),
            ("Longitude:", "lon"),
            ("Heading deg T:", "hdg"),
            ("Speed kn:", "spd"),
            ("Wind dir deg T:", "wind_dir"),
            ("Wind speed kn:", "wind_spd"),
        ]
        for i, (label, field_name) in enumerate(labels):
            y = 120 + i * 40
            self.screen.blit(self.font_small.render(label, True, (255, 255, 255)), (40, y + 6))
            field = self.input_fields[field_name]
            color = (100, 220, 100) if field["active"] else (120, 120, 120)
            pg.draw.rect(self.screen, color, field["rect"], 2)
            self.screen.blit(self.font_small.render(field["value"], True, (255, 255, 255)), (field["rect"].x + 5, y + 6))

        nmea = self.cfg.get("nmea_output", {})
        nmea_text = f"NMEA output: {'ON' if nmea.get('enabled') else 'OFF'}  {nmea.get('host')}:{nmea.get('port')}"
        self.screen.blit(self.font_small.render(nmea_text, True, (255, 220, 120)), (40, 410))
        self.screen.blit(self.font_small.render("SPACE: start/cycle screens  |  Click fields to edit", True, (220, 220, 220)), (40, 540))

    def _draw_controls(self) -> None:
        self.screen.fill((0, 70, 80))
        self.screen.blit(self.font_big.render("CONTROL PANEL", True, (255, 255, 255)), (40, 40))
        lines = [
            f"Heading: {self.ship.heading:.1f} deg T",
            f"Speed:   {self.ship.speed:.1f} kn",
            f"Lat/Lon: {self.ship.lat:.6f}, {self.ship.lon:.6f}",
            "Future: engine telegraph, rudder, autopilot, alarms",
        ]
        for i, line in enumerate(lines):
            self.screen.blit(self.font.render(line, True, (230, 255, 255)), (60, 120 + i * 40))

    def _draw_visual(self) -> None:
        self.screen.fill((40, 80, 120))
        horizon_y = 260
        pg.draw.rect(self.screen, (80, 150, 210), pg.Rect(0, 0, 1100, horizon_y))
        pg.draw.rect(self.screen, (10, 50, 90), pg.Rect(0, horizon_y, 1100, 618 - horizon_y))
        self.screen.blit(self.font_big.render("VISUAL WINDOW", True, (255, 255, 255)), (40, 40))
        self.screen.blit(self.font.render("Placeholder bridge view - next phase will add vessel/sea/targets", True, (255, 255, 255)), (40, 100))


if __name__ == "__main__":
    import sys

    headless = True
    if "--window" in sys.argv or "--gui" in sys.argv or "--no-headless" in sys.argv:
        headless = False
    if "--headless" in sys.argv:
        headless = True

    App(headless=headless).run()
