import pygame as pg
from .utils import clamp


class Controls:
    """Centralizes keyboard hotkeys and per-screen input mapping."""

    def handle(self, app, dt, events):
        for e in events:
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                app._cycle_state()

        keys = pg.key.get_pressed()
        if app.state == 'radar':
            self._radar_hotkeys(app, keys)
        if app.state == 'ecdis' and keys[pg.K_r]:
            app.ecdis.reload_chart()

    def _radar_hotkeys(self, app, keys):
        r = app.radar
        if keys[pg.K_g]:
            if keys[pg.K_RIGHT]:
                r.gain = clamp(r.gain + 10, 0, 100)
            if keys[pg.K_LEFT]:
                r.gain = clamp(r.gain - 10, 0, 100)
        if keys[pg.K_s]:
            if keys[pg.K_RIGHT]:
                r.anti_sea = clamp(r.anti_sea + 1, 0, 100)
            if keys[pg.K_LEFT]:
                r.anti_sea = clamp(r.anti_sea - 1, 0, 100)
        if keys[pg.K_h]:
            if keys[pg.K_RIGHT]:
                r.ship.heading = (r.ship.heading + 1) % 360
                r.fixed_heading = r.ship.heading
                r._grid_cache = None
            if keys[pg.K_LEFT]:
                r.ship.heading = (r.ship.heading - 1) % 360
                r.fixed_heading = r.ship.heading
                r._grid_cache = None
        if keys[pg.K_e]:
            if keys[pg.K_RIGHT]:
                r.ebl_bearing = (r.ebl_bearing + 1) % 360
            if keys[pg.K_LEFT]:
                r.ebl_bearing = (r.ebl_bearing - 1) % 360
        if keys[pg.K_v]:
            if keys[pg.K_RIGHT]:
                r.vrm_radius_nm = min(r.vrm_radius_nm + 0.1, 48)
            if keys[pg.K_LEFT]:
                r.vrm_radius_nm = max(r.vrm_radius_nm - 0.1, 0.1)
