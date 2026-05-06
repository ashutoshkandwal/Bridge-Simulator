import pygame as pg
from pygame import RESIZABLE

from bridge_sim.radar import RadarDisplay
from bridge_sim.ecdis import ECDISDisplay
from bridge_sim.controls import Controls
from bridge_sim.utils import load_config, load_last_scenario, save_last_scenario
from bridge_sim.models import Ship

class App:
    def __init__(self, headless=False):
        self.headless = headless
        
        if not headless:
            pg.init()
            self.clock = pg.time.Clock()
            self.screen = pg.display.set_mode((1100, 618), RESIZABLE)
            pg.display.set_caption("MAIN MENU")
        else:
            # Headless mode: no PyGame window, just web servers
            import time
            self.clock = None
            self.screen = None

        self.cfg = load_config()  # <— loads config.json if present

        # Ensure the Web Radar server (web menu + viewers) is available immediately
        # so http://127.0.0.1:5001/ works even before leaving this desktop menu.
        try:
            from bridge_sim import web_radar
            web_radar.start_web_radar(host='127.0.0.1', port=5001, open_browser=True)
            print("[MAIN] ✓ Web RADAR (web menu) started - http://127.0.0.1:5001/")
        except Exception as e:
            print(f"[MAIN] ✗ Failed to pre-start Web RADAR: {e}")

        # Also start the Web ECDIS server on port 5000 so menu can open it
        try:
            from bridge_sim import web_ecdis
            if web_ecdis.start_web_ecdis(host='127.0.0.1', port=5000, open_browser=False):
                print("[MAIN] ✓ Web ECDIS started - http://127.0.0.1:5000/")
            else:
                print("[MAIN] ✗ Failed to start web ECDIS")
        except Exception as e:
            print(f"[MAIN] ✗ Web ECDIS startup error: {e}")

        self.state = 'menu'  # 'menu'|'radar'|'ecdis'|'controls'
        
        # Ship initialization values (centered in US4MD20M chart - Chesapeake Bay)
        # Chart bounds: lat 37.857-38.409 N, lon -76.494 to -75.373 W
        self.ship_lat = 38.15  # East side - in open water with land visible
        self.ship_lon = -75.60  # Offshore position
        self.ship_heading = 45.0
        self.ship_speed = 12.0
        # Environmental (wind) defaults
        self.wind_dir = 0.0   # deg True (from)
        self.wind_speed = 0.0  # knots - start at 0 to see effect when increased
        # When true, ECDIS shows the menu-entered course/speed (static),
        # even if in-sim controls change heading/speed later.
        self.static_course_speed = True
        
        # Load last-used values if present
        last = load_last_scenario() or {}
        def val(key, default):
            return str(last.get(key, default))

        # Input field tracking (for menu) - two columns layout
        self.input_fields = {
            # Left column: Ship data
            'lat': {'value': val('lat', self.ship_lat), 'active': False, 'rect': pg.Rect(250, 120, 150, 30)},
            'lon': {'value': val('lon', self.ship_lon), 'active': False, 'rect': pg.Rect(250, 160, 150, 30)},
            'hdg': {'value': val('hdg', self.ship_heading), 'active': False, 'rect': pg.Rect(250, 200, 150, 30)},
            'spd': {'value': val('spd', self.ship_speed), 'active': False, 'rect': pg.Rect(250, 240, 150, 30)},
            # Left column: Wind
            'wind_dir': {'value': val('wind_dir', self.wind_dir), 'active': False, 'rect': pg.Rect(250, 300, 150, 30)},
            'wind_spd': {'value': val('wind_spd', self.wind_speed), 'active': False, 'rect': pg.Rect(250, 340, 150, 30)},
            # Right column: Target 1
            't1_rng': {'value': val('t1_rng', '3.0'), 'active': False, 'rect': pg.Rect(650, 120, 150, 30)},
            't1_brg': {'value': val('t1_brg', '045'), 'active': False, 'rect': pg.Rect(650, 160, 150, 30)},
            't1_crs': {'value': val('t1_crs', '090'), 'active': False, 'rect': pg.Rect(650, 200, 150, 30)},
            't1_spd': {'value': val('t1_spd', '12.0'), 'active': False, 'rect': pg.Rect(650, 240, 150, 30)},
            # Right column: Target 2
            't2_rng': {'value': val('t2_rng', '6.0'), 'active': False, 'rect': pg.Rect(650, 320, 150, 30)},
            't2_brg': {'value': val('t2_brg', '315'), 'active': False, 'rect': pg.Rect(650, 360, 150, 30)},
            't2_crs': {'value': val('t2_crs', '270'), 'active': False, 'rect': pg.Rect(650, 400, 150, 30)},
            't2_spd': {'value': val('t2_spd', '16.0'), 'active': False, 'rect': pg.Rect(650, 440, 150, 30)},
        }
        self.menu_ready = False
        
        self.radar = None
        self.ecdis = None
        self.controls = Controls() if not headless else None
        self.web_ecdis_enabled = True  # Set to True to use web ECDIS

        # displays will be initialized when cycling from menu

        if not headless:
            self.font_big = pg.font.SysFont(None, 50)
            self.font = pg.font.SysFont(None, 24)
            self.font_small = pg.font.SysFont(None, 18)
        else:
            self.font_big = None
            self.font = None
            self.font_small = None

        # Target specs (initialized after menu confirm)
        self.target_specs = []  # list of dicts: {range_nm, bearing_deg, course_deg, speed_kn, x_nm, y_nm}
        self.sim_start_time = None
        # Time scale for target motion integration (1.0 = real-time)
        # Increase temporarily only for demos if needed.
        self.sim_time_scale = 1.0

    def run(self):
        if self.headless:
            # Headless mode: just keep servers running
            print("[MAIN] Running in headless mode - use web interface at http://127.0.0.1:5001/")
            print("[MAIN] Press Ctrl+C to stop")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[MAIN] Shutting down...")
            return
        
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            events = pg.event.get()
            for e in events:
                if e.type == pg.QUIT:
                    running = False

            if self.state == 'menu':
                self._handle_menu_input(events)
                self._draw_menu()
            else:
                self.controls.handle(self, dt, events)
                
                # Update ship position for non-menu states
                if self.radar and self.radar.ship:
                    self.radar.ship.update_position(dt, north=0)
                    
                    # Push updates to web ECDIS if enabled
                    if self.web_ecdis_enabled:
                        try:
                            from bridge_sim import web_ecdis
                            ship = self.radar.ship
                            # Use static course/speed from menu if requested
                            send_heading = self.ship_heading if self.static_course_speed else ship.heading
                            send_speed = self.ship_speed if self.static_course_speed else ship.speed
                            web_ecdis.update_ship(ship.lat, ship.lon, send_heading, send_speed)
                        except Exception:
                            pass

                    # Push user-defined targets to Web RADAR
                    try:
                        from bridge_sim import web_radar
                        if web_radar.is_web_radar_running():
                            heading = self.ship_heading if self.static_course_speed else self.radar.ship.heading
                            speed = self.ship_speed if self.static_course_speed else self.radar.ship.speed
                            
                            # Debug: print heading/speed every 60 frames
                            if hasattr(self, '_debug_counter'):
                                self._debug_counter += 1
                            else:
                                self._debug_counter = 0
                            if self._debug_counter % 60 == 0:
                                print(f"[MAIN DEBUG] Pushing to web radar: heading={heading}°, speed={speed} kn")
                            
                            # Update positions based on ground motion
                            # Own ship movement vector (NM/sec)
                            import math
                            own_vx = (speed / 3600.0) * math.sin(math.radians(heading))
                            own_vy = (speed / 3600.0) * math.cos(math.radians(heading))
                            
                            # Use the live radar server's current display parameters
                            try:
                                from web.radar_server import radar_state, radar_lock
                                with radar_lock:
                                    ppi_radius = radar_state.get('ppi_radius', 250)
                                    display_range_nm = radar_state.get('range_nm', 12.0)
                                    north_up = radar_state.get('north_up', True)
                                    fixed_heading = radar_state.get('fixed_heading', 0.0)
                                    motion_mode = radar_state.get('motion', 'RM')
                            except Exception:
                                ppi_radius = 250
                                display_range_nm = 12.0
                                north_up = True
                                fixed_heading = 0.0
                                motion_mode = 'RM'

                            # Detect motion mode transition to True Motion; reset ground position to avoid jump
                            if not hasattr(self, '_last_motion_mode'):
                                self._last_motion_mode = motion_mode
                            if motion_mode == 'TM' and self._last_motion_mode != 'TM':
                                # Reset ground track so ship starts from current displayed center
                                self.ship_ground_x_nm = 0.0
                                self.ship_ground_y_nm = 0.0
                            self._last_motion_mode = motion_mode
                            
                            # Initialize ship ground position tracker if needed
                            if not hasattr(self, 'ship_ground_x_nm'):
                                self.ship_ground_x_nm = 0.0
                                self.ship_ground_y_nm = 0.0
                            
                            # Update ship ground position
                            self.ship_ground_x_nm += own_vx * dt * self.sim_time_scale
                            self.ship_ground_y_nm += own_vy * dt * self.sim_time_scale
                            
                            # Ship pixel position depends on motion mode
                            if motion_mode == 'TM':
                                # True Motion: ship moves on display based on ground position
                                ship_rng_nm = math.hypot(self.ship_ground_x_nm, self.ship_ground_y_nm)
                                ship_bearing = (math.degrees(math.atan2(self.ship_ground_x_nm, self.ship_ground_y_nm)) + 360) % 360
                                display_bearing = ship_bearing if north_up else (ship_bearing - fixed_heading + 360) % 360
                                ship_rng_px = (ship_rng_nm / display_range_nm) * ppi_radius
                                ship_px_x = 300 + ship_rng_px * math.sin(math.radians(display_bearing))
                                ship_px_y = 300 - ship_rng_px * math.cos(math.radians(display_bearing))
                            else:
                                # Relative Motion: ship stays at center
                                ship_px_x, ship_px_y = 300, 300
                            
                            targets = []
                            for spec in self.target_specs:
                                # Target ground velocity (NM/sec)
                                tvx = spec['speed_kn'] / 3600.0 * math.sin(math.radians(spec['course_deg']))
                                tvy = spec['speed_kn'] / 3600.0 * math.cos(math.radians(spec['course_deg']))
                                
                                if motion_mode == 'TM':
                                    # True Motion: integrate absolute ground positions
                                    spec['x_nm'] += tvx * dt * self.sim_time_scale
                                    spec['y_nm'] += tvy * dt * self.sim_time_scale
                                else:
                                    # Relative Motion: integrate relative to own ship
                                    rvx = tvx - own_vx
                                    rvy = tvy - own_vy
                                    spec['x_nm'] += rvx * dt * self.sim_time_scale
                                    spec['y_nm'] += rvy * dt * self.sim_time_scale
                                
                                rng_nm = math.hypot(spec['x_nm'], spec['y_nm'])
                                bearing_deg = (math.degrees(math.atan2(spec['x_nm'], spec['y_nm'])) + 360) % 360
                                
                                # Apply Course Up rotation if needed
                                display_bearing = bearing_deg
                                if not north_up:
                                    display_bearing = (bearing_deg - fixed_heading + 360) % 360
                                
                                # Convert to pixel position relative to center (not ship)
                                rng_px = (rng_nm / display_range_nm) * ppi_radius
                                px = 300 + rng_px * math.sin(math.radians(display_bearing))
                                py = 300 - rng_px * math.cos(math.radians(display_bearing))
                                targets.append({
                                    'x': px, 'y': py, 'bearing': bearing_deg, 'range_nm': rng_nm,
                                    'course': spec['course_deg'], 'speed': spec['speed_kn']
                                })
                            # Generate sea clutter influenced by wind and display orientation
                            try:
                                north = 0.0 if north_up else fixed_heading
                                # Points count scales with wind and range
                                wind_factor = min(2.0, 0.3 + max(0.0, self.wind_speed) / 20.0)
                                base_points = int(800 * (display_range_nm / 12.0) * wind_factor)
                                r_min = 0.03 * ppi_radius
                                r_max = 0.6 * ppi_radius
                                import random, math
                                clutter_pts = []
                                for _ in range(base_points):
                                    # Angle biased around wind_dir (FROM) with some spread
                                    ang_true = (self.wind_dir + random.gauss(0, 25)) % 360.0
                                    ang_display = (ang_true - north + 360.0) % 360.0
                                    # Radius concentrated near center (sea echo near-range)
                                    u = random.random()
                                    r = r_min + (u ** 1.5) * (r_max - r_min)
                                    x = 300 + r * math.sin(math.radians(ang_display))
                                    y = 300 - r * math.cos(math.radians(ang_display))
                                    # Keep within PPI circle
                                    if math.hypot(x - 300, y - 300) <= ppi_radius:
                                        clutter_pts.append({'x': int(x), 'y': int(y)})
                            except Exception:
                                clutter_pts = []

                            # Reflect updated wind to server state and broadcast
                            try:
                                from web.radar_server import radar_state, radar_lock, broadcast_radar_state
                                with radar_lock:
                                    radar_state['wind_dir'] = float(self.wind_dir)
                                    radar_state['wind_speed'] = float(self.wind_speed)
                                    # Update ship geodetic position for 3D bridge view
                                    if hasattr(self.radar, 'ship'):
                                        radar_state['ship']['lat'] = float(self.radar.ship.lat)
                                        radar_state['ship']['lon'] = float(self.radar.ship.lon)
                                    # SEA (anti-sea clutter) is now controlled ONLY from radar panel
                                # Broadcast after releasing lock
                                broadcast_radar_state()
                            except Exception:
                                pass

                            web_radar.push_radar_update(ship_px_x, ship_px_y, heading, speed, targets=targets, clutter=clutter_pts)
                            
                            # Update bridge controls
                            try:
                                from web.radar_server import update_bridge_data
                                # Calculate rate of turn (simplified - would need history for real calculation)
                                rot = 0.0  # TODO: calculate from heading changes
                                rudder_angle = 0.0  # TODO: get from ship controls if available
                                rpm = int(speed * 8)  # Rough approximation: 8 RPM per knot
                                update_bridge_data(heading, speed, rpm, rot, rudder_angle)
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"[MAIN] Web radar update error: {e}")
                        import traceback
                        traceback.print_exc()

                if self.state == 'radar':
                    self.radar.update(dt, events); self._draw_radar()
                elif self.state == 'ecdis':
                    self._draw_ecdis()
                elif self.state == 'controls':
                    self._draw_controls()

            pg.display.flip()
        pg.quit()

    def _cycle_state(self):
        if self.state == 'menu' and not self.menu_ready:
            return  # Don't advance until menu is complete
        
        # Initialize displays on first transition from menu
        if self.state == 'menu' and self.radar is None:
            ship = Ship(320, 310, self.ship_heading, self.ship_speed, self.ship_lat, self.ship_lon)
            self.radar = RadarDisplay(self.screen, cfg=self.cfg, ship=ship)
            self.ecdis = ECDISDisplay(self.screen, ship=ship)
            
            # Try to load NOAA ENC chart if available
            import os
            enc_path = os.path.join("bridge_sim", "areas", "noaa_charts", "US4MD20M.000")
            if os.path.exists(enc_path):
                print(f"[MAIN] Loading ENC: {enc_path}")
                if self.ecdis.load_noaa_enc(enc_path):
                    print("[MAIN] ✓ ENC loaded successfully")
                else:
                    print("[MAIN] ✗ Failed to load ENC")
            else:
                print(f"[MAIN] ENC not found at {enc_path} (using PNG/fallback)")
            
            # Web servers already started in __init__, so just initialize state
            # Set initial environmental state on radar server
            try:
                from web.radar_server import radar_state, radar_lock
                import time
                time.sleep(0.5)  # Give servers time to fully start
                with radar_lock:
                    radar_state['wind_dir'] = float(self.wind_dir)
                    radar_state['wind_speed'] = float(self.wind_speed)
            except Exception as e:
                print(f"[MAIN] Warning: Could not set wind state: {e}")
            
            # Push initial radar state
            try:
                from bridge_sim import web_radar
                web_radar.push_radar_update(300, 300, self.ship_heading, self.ship_speed, targets=[], clutter=[])
                print(f"[MAIN] Initial radar state: heading={self.ship_heading}°, speed={self.ship_speed} kn")
            except Exception as e:
                print(f"[MAIN] Radar update error: {e}")
            
            # Initialize bridge controls with menu values
            try:
                from web.radar_server import update_bridge_data
                update_bridge_data(
                    heading=self.ship_heading,
                    speed=self.ship_speed,
                    rpm=0,
                    rot=0.0,
                    rudder_angle=0.0
                )
                print(f"[MAIN] Initial bridge controls: heading={self.ship_heading}°, speed={self.ship_speed} kn")
            except Exception as e:
                print(f"[MAIN] Bridge controls init error: {e}")
            
            # Initialize ECDIS position
            if self.web_ecdis_enabled:
                try:
                    from bridge_sim import web_ecdis
                    send_heading = self.ship_heading
                    send_speed = self.ship_speed
                    web_ecdis.update_ship(self.ship_lat, self.ship_lon, send_heading, send_speed)
                    print(f"[MAIN] Initial ECDIS state: lat={self.ship_lat}, lon={self.ship_lon}")
                except Exception as e:
                    print(f"[MAIN] ECDIS update error: {e}")
        
        order = ['menu', 'radar', 'ecdis', 'controls']
        i = order.index(self.state); self.state = order[(i+1) % len(order)]
        if self.state == 'radar':
            pg.display.set_caption("RADAR TRAINING AID"); self.radar.on_show()
        else:
            if self.radar:
                self.radar.on_hide()
            pg.display.set_caption(self.state.upper())

    def _draw_menu(self):
        self.screen.fill((0, 0, 100))
        txt = self.font_big.render("SHIP SETUP", True, (255, 255, 255))
        self.screen.blit(txt, (40, 20))
        
        # Left column: Ship data
        ship_label = self.font.render("OWN SHIP", True, (200, 255, 200))
        self.screen.blit(ship_label, (40, 80))

        ship_labels = ['Latitude (°N):', 'Longitude (°W):', 'Heading (°T):', 'Speed (kn):', 'Wind Dir (°T):', 'Wind Speed (kn):']
        ship_fields = ['lat', 'lon', 'hdg', 'spd', 'wind_dir', 'wind_spd']
        y_start = 120
        
        for idx, (label, field) in enumerate(zip(ship_labels, ship_fields)):
            y = y_start + idx * 40
            label_surf = self.font_small.render(label, True, (255, 255, 255))
            self.screen.blit(label_surf, (40, y + 5))
            
            rect = self.input_fields[field]['rect']
            rect.y = y
            color = (100, 200, 100) if self.input_fields[field]['active'] else (100, 100, 100)
            pg.draw.rect(self.screen, color, rect, 2)
            
            value_text = self.font_small.render(self.input_fields[field]['value'], True, (255, 255, 255))
            self.screen.blit(value_text, (rect.x + 5, rect.y + 5))
        
        # Right column: Targets
        target_label = self.font.render("TARGETS", True, (255, 200, 200))
        self.screen.blit(target_label, (440, 80))
        
        # Target 1
        t1_title = self.font_small.render("Target 1", True, (220, 220, 150))
        self.screen.blit(t1_title, (440, 105))
        
        target_labels = ['Range (NM):', 'Bearing (°):', 'Course (°):', 'Speed (kn):']
        t1_fields = ['t1_rng', 't1_brg', 't1_crs', 't1_spd']
        
        for idx, (label, field) in enumerate(zip(target_labels, t1_fields)):
            y = y_start + idx * 40
            label_surf = self.font_small.render(label, True, (255, 255, 255))
            self.screen.blit(label_surf, (440, y + 5))
            
            rect = self.input_fields[field]['rect']
            rect.y = y
            color = (100, 200, 100) if self.input_fields[field]['active'] else (100, 100, 100)
            pg.draw.rect(self.screen, color, rect, 2)
            
            value_text = self.font_small.render(self.input_fields[field]['value'], True, (255, 255, 255))
            self.screen.blit(value_text, (rect.x + 5, rect.y + 5))
        
        # Target 2
        t2_y_start = y_start + 4 * 40 + 40  # 40px gap after T1
        t2_title = self.font_small.render("Target 2", True, (220, 220, 150))
        self.screen.blit(t2_title, (440, t2_y_start - 15))
        
        t2_fields = ['t2_rng', 't2_brg', 't2_crs', 't2_spd']
        
        for idx, (label, field) in enumerate(zip(target_labels, t2_fields)):
            y = t2_y_start + idx * 40
            label_surf = self.font_small.render(label, True, (255, 255, 255))
            self.screen.blit(label_surf, (440, y + 5))
            
            rect = self.input_fields[field]['rect']
            rect.y = y
            color = (100, 200, 100) if self.input_fields[field]['active'] else (100, 100, 100)
            pg.draw.rect(self.screen, color, rect, 2)
            
            value_text = self.font_small.render(self.input_fields[field]['value'], True, (255, 255, 255))
            self.screen.blit(value_text, (rect.x + 5, rect.y + 5))
        
        # Draw instructions
        instruction = "Click to edit • ENTER: next field • SPACE: start" if not self.menu_ready else "SPACE to continue"
        inst_surf = self.font_small.render(instruction, True, (200, 200, 100))
        self.screen.blit(inst_surf, (40, 530))
        
        if self.menu_ready:
            ready_surf = self.font.render("✓ Ready to Start", True, (100, 255, 100))
            self.screen.blit(ready_surf, (40, 560))
            hint = self.font_small.render("Targets will appear on radar with entered motion", True, (180, 220, 180))
            self.screen.blit(hint, (40, 585))
    
    def _handle_menu_input(self, events):
        for e in events:
            if e.type == pg.MOUSEBUTTONDOWN:
                for field_name, field_data in self.input_fields.items():
                    if field_data['rect'].collidepoint(e.pos):
                        for f in self.input_fields.values():
                            f['active'] = False
                        field_data['active'] = True
            
            if e.type == pg.KEYDOWN:
                # Find active field
                active_field = None
                for field_name, field_data in self.input_fields.items():
                    if field_data['active']:
                        active_field = field_name
                        break
                
                if active_field:
                    if e.key == pg.K_RETURN:
                        # Validate and move to next field
                        try:
                            val = float(self.input_fields[active_field]['value'])
                            field_order = ['lat', 'lon', 'hdg', 'spd', 'wind_dir', 'wind_spd',
                                         't1_rng', 't1_brg', 't1_crs', 't1_spd',
                                         't2_rng', 't2_brg', 't2_crs', 't2_spd']
                            curr_idx = field_order.index(active_field)
                            if curr_idx < len(field_order) - 1:
                                self.input_fields[field_order[curr_idx + 1]]['active'] = True
                            self.input_fields[active_field]['active'] = False
                        except ValueError:
                            self.input_fields[active_field]['value'] = ""
                    
                    elif e.key == pg.K_BACKSPACE:
                        self.input_fields[active_field]['value'] = self.input_fields[active_field]['value'][:-1]
                    
                    elif e.unicode.isdigit() or e.unicode in '.-':
                        self.input_fields[active_field]['value'] += e.unicode
            
            if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                # Validate all fields
                try:
                    self.ship_lat = float(self.input_fields['lat']['value'])
                    self.ship_lon = float(self.input_fields['lon']['value'])
                    self.ship_heading = float(self.input_fields['hdg']['value'])
                    self.ship_speed = float(self.input_fields['spd']['value'])
                    # Wind
                    self.wind_dir = float(self.input_fields['wind_dir']['value']) % 360.0
                    self.wind_speed = max(0.0, float(self.input_fields['wind_spd']['value']))
                    # Parse targets
                    import math
                    specs = []
                    for prefix in ['t1','t2']:
                        try:
                            rng = float(self.input_fields[f'{prefix}_rng']['value'])
                            brg = float(self.input_fields[f'{prefix}_brg']['value'])
                            crs = float(self.input_fields[f'{prefix}_crs']['value'])
                            spd = float(self.input_fields[f'{prefix}_spd']['value'])
                        except (ValueError, KeyError):
                            continue
                        # Convert range/bearing to NM Cartesian relative coords (x east, y north)
                        x_nm = rng * math.sin(math.radians(brg))
                        y_nm = rng * math.cos(math.radians(brg))
                        specs.append({
                            'range_nm': rng,
                            'bearing_deg': brg,
                            'course_deg': crs,
                            'speed_kn': spd,
                            'x_nm': x_nm,
                            'y_nm': y_nm
                        })
                    # Persist last-used values
                    save_last_scenario({k: v['value'] for k, v in self.input_fields.items()})
                    self.target_specs = specs
                    self.sim_start_time = pg.time.get_ticks()/1000.0
                    self.menu_ready = True
                    self._cycle_state()
                except ValueError:
                    pass  # Invalid input, don't advance

    def _draw_ecdis(self):
        self.ecdis.draw(self.radar.ship)

    def _draw_controls(self):
        self.screen.fill((0,100,100))
        txt = self.font_big.render("CONTROLS (placeholder)", True, (255,255,255))
        self.screen.blit(txt, (40, 40))

    def _draw_radar(self):
        self.radar.draw()

if __name__ == "__main__":
    import sys
    # Default to headless unless explicitly requested otherwise.
    # Use: --window or --gui or --no-headless to force a windowed run.
    headless = True
    if '--window' in sys.argv or '--gui' in sys.argv or '--no-headless' in sys.argv:
        headless = False
    # Backwards-compatible: if user passed explicit --headless, keep headless
    if '--headless' in sys.argv:
        headless = True

    App(headless=headless).run()
