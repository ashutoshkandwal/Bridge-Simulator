"""Minimal Pygame radar display module.

This module restores the package structure expected by main.py. The more advanced
web radar remains in web/radar_server.py.
"""

import math
import pygame as pg


class RadarDisplay:
    def __init__(self, screen, cfg=None, ship=None):
        self.screen = screen
        self.cfg = cfg or {}
        self.ship = ship
        self.range_nm = 12.0
        self.gain = 30
        self.anti_sea = 0
        self.fixed_heading = getattr(ship, 'heading', 0.0) if ship else 0.0
        self.ebl_bearing = 45.0
        self.vrm_radius_nm = 2.0
        self._grid_cache = None
        self.font = pg.font.SysFont(None, 22)

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def nm_to_px(self, nm):
        return nm * 250.0 / max(0.1, self.range_nm)

    def spd_to_px_per_s(self, speed_kn):
        return self.nm_to_px(speed_kn / 3600.0)

    def update(self, dt, events):
        # Placeholder for advanced desktop radar behaviour.
        pass

    def draw(self):
        self.screen.fill((5, 20, 10))
        cx, cy = 300, 300
        radius = 250
        pg.draw.circle(self.screen, (28, 179, 2), (cx, cy), radius, 2)
        for frac in (0.25, 0.5, 0.75):
            pg.draw.circle(self.screen, (28, 80, 20), (cx, cy), int(radius * frac), 1)
        pg.draw.line(self.screen, (28, 80, 20), (cx - radius, cy), (cx + radius, cy), 1)
        pg.draw.line(self.screen, (28, 80, 20), (cx, cy - radius), (cx, cy + radius), 1)

        if self.ship:
            pg.draw.circle(self.screen, (255, 255, 0), (cx, cy), 5)
            hdg = math.radians(self.ship.heading)
            pg.draw.line(self.screen, (255, 255, 0), (cx, cy), (cx + 25 * math.sin(hdg), cy - 25 * math.cos(hdg)), 2)
            txt = f"HDG {self.ship.heading:05.1f}  SPD {self.ship.speed:.1f} kn"
            self.screen.blit(self.font.render(txt, True, (28, 179, 2)), (20, 20))
