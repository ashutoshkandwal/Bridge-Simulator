
import os
from typing import Tuple
import pygame as pg

class ECDISDisplay:
    def __init__(self, screen: pg.Surface, ship=None, ship_lat: float = 36.15, ship_lon: float = -5.50, follow_ship: bool = False):
        self.screen = screen
        self.ship = ship
        self.follow_ship = follow_ship
        self.view = pg.Rect(10, 10, 900, 598)
        
        # Use ship object or fallback to initial lat/lon
        if ship is not None:
            ship_lat = ship.lat
            ship_lon = ship.lon
        
        # Set chart bounds around ship position with some margin
        margin = 0.4  # degrees
        self.latN, self.lonW = ship_lat + margin, ship_lon - margin
        self.latS, self.lonE = ship_lat - margin, ship_lon + margin

        self.chart_img = None
        self.chart_status = ""
        self._discover_and_load_chart()

        self.enc_layers = {}  # For NOAA ENC vector layers

        self.fallback_coast = [
            (36.19, -6.03), (36.17, -5.90), (36.15, -5.80), (36.14, -5.70), (36.13, -5.60),
            (36.13, -5.50), (36.10, -5.45), (36.10, -5.35), (36.11, -5.32), (36.13, -5.30), (36.14, -5.28),
            (36.08, -5.40), (36.04, -5.45), (36.00, -5.50), (35.98, -5.55), (35.95, -5.60),
            (35.93, -5.70), (35.92, -5.80), (35.90, -5.90), (35.88, -6.00)
        ]

        self.font20 = pg.font.SysFont(None, 20)
        self.font28 = pg.font.SysFont(None, 28)

        self.grid_color = (40, 120, 180)
        self.land_color = (60, 60, 60)
        self.water_bg = (5, 30, 40)
        self.text_color = (200, 220, 230)
        
        # One-time debug log flag
        self._debug_log_shown = False

    def _possible_chart_paths(self):
        paths = []
        base = None
        
        try:
            base = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            pass
        
        cwd = os.getcwd()
        
        # Priority 1: Check areas subfolder first (most likely location)
        if base:
            areas_subfolder = os.path.join(base, 'areas')
            if os.path.isdir(areas_subfolder):
                try:
                    # First look for any image file with 'gibr' in name
                    for f in os.listdir(areas_subfolder):
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            full_path = os.path.join(areas_subfolder, f)
                            paths.append(full_path)
                except Exception:
                    pass
        
        # Priority 2: Check root bridge_sim folder
        if base:
            try:
                for f in os.listdir(base):
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        full_path = os.path.join(base, f)
                        if full_path not in paths:
                            paths.append(full_path)
            except Exception:
                pass
        
        # Priority 3: Check current working directory
        try:
            for f in os.listdir(cwd):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    full_path = os.path.join(cwd, f)
                    if full_path not in paths:
                        paths.append(full_path)
        except Exception:
            pass
        
        # Remove duplicates while preserving order
        seen = set()
        unique_paths = []
        for p in paths:
            if p not in seen:
                unique_paths.append(p)
                seen.add(p)
        
        return unique_paths

    def _discover_and_load_chart(self):
        self.chart_img = None
        self.chart_status = ""
        
        possible_paths = self._possible_chart_paths()
        
        if not possible_paths:
            self.chart_status = "No chart files found in areas/ folder. Using schematic coastline."
            return
        
        tried = []
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    print(f"[ECDIS] Trying to load: {p}")
                    img = pg.image.load(p)
                    print(f"[ECDIS] Loaded image: {os.path.basename(p)} ({img.get_size()})")
                    
                    # Convert to appropriate format
                    if img.get_alpha() is not None:
                        img = img.convert_alpha()
                    else:
                        img = img.convert()
                    
                    # If a same-named JSON sidecar exists, use it for georeference
                    meta = None
                    base_noext = os.path.splitext(p)[0]
                    meta_path = base_noext + '.json'
                    if os.path.exists(meta_path):
                        try:
                            import json
                            with open(meta_path, 'r', encoding='utf-8') as fh:
                                meta = json.load(fh)
                            # Expect keys latN, latS, lonW, lonE
                            if all(k in meta for k in ('latN','latS','lonW','lonE')):
                                self.latN = float(meta['latN'])
                                self.latS = float(meta['latS'])
                                self.lonW = float(meta['lonW'])
                                self.lonE = float(meta['lonE'])
                                print(f"[ECDIS] Applied georeference from {os.path.basename(meta_path)} -> bounds=({self.latN},{self.latS},{self.lonW},{self.lonE})")
                        except Exception as e:
                            print(f"[ECDIS] Failed to read metadata {meta_path}: {e}")

                    # Scale to display size (chart is assumed to be full-frame for the view)
                    self.chart_img = pg.transform.smoothscale(img, (self.view.width, self.view.height))
                    self.chart_status = f"Loaded: {os.path.basename(p)}"
                    print(f"[ECDIS] ✓ Chart loaded successfully!")
                    return
                except Exception as e:
                    error_msg = f"{os.path.basename(p)} -> {str(e)[:50]}"
                    tried.append(error_msg)
                    print(f"[ECDIS] Failed to load {os.path.basename(p)}: {e}")
        
        # If we get here, no chart loaded
        if tried:
            self.chart_status = "No valid chart image. Using schematic coastline. (Tried: " + "; ".join(tried[:2]) + ("..." if len(tried)>2 else "") + ")"
        else:
            self.chart_status = "No chart files found. Using schematic coastline."
        print(f"[ECDIS] {self.chart_status}")

    def reload_chart(self):
        self._discover_and_load_chart()

    def load_noaa_enc(self, enc_path: str):
        """
        Load a NOAA ENC chart (S-57/S-101 format) and extract key layers.
        
        Sets self.latN, self.latS, self.lonW, self.lonE from chart bounds.
        Stores vector layers in self.enc_layers for rendering.
        
        Args:
            enc_path: Path to .000 (S-57) or .gpkg (S-101) file
        """
        try:
            from tools.noaa_enc_loader import ENChart
        except ImportError as e:
            print(f"[ECDIS] ENC loader not available: {e}")
            print(f"[ECDIS] Ensure GDAL, fiona, shapely are installed in gdal_env")
            self.enc_layers = {}
            return False
        
        try:
            print(f"[ECDIS] Loading ENC: {enc_path}")
            chart = ENChart(enc_path)
            
            # Extract bounds and set view
            latN, latS, lonW, lonE = chart.get_bounds()
            self.latN, self.latS, self.lonW, self.lonE = latN, latS, lonW, lonE
            print(f"[ECDIS] ENC bounds: lat {latS:.3f}..{latN:.3f}, lon {lonW:.3f}..{lonE:.3f}")
            
            # Load key layers for rendering
            self.enc_layers = {}
            # Actual S-57 layer names from the chart
            layer_names = ['LNDARE', 'DEPCNT', 'SLCONS', 'COALNE', 'BOYLAT', 'LIGHTS']
            print(f"[ECDIS] Will attempt layers: {layer_names}")
            
            for layer_name in layer_names:
                if layer_name in chart.layers:
                    try:
                        geoms = chart.get_layer(layer_name)
                        self.enc_layers[layer_name] = geoms
                        print(f"[ECDIS] Loaded layer {layer_name}: {len(geoms)} geometries")
                    except Exception as e:
                        print(f"[ECDIS] Failed to load layer {layer_name}: {e}")
            
            print(f"[ECDIS] ✓ ENC loaded successfully with {len(self.enc_layers)} layers")
            if self.enc_layers:
                # Auto-adjust ship start position if we have a ship object and it sits outside the ENC bounds
                if self.ship is not None:
                    if not (self.latS <= self.ship.lat <= self.latN and self.lonW <= self.ship.lon <= self.lonE):
                        center_lat = (self.latN + self.latS) / 2.0
                        center_lon = (self.lonW + self.lonE) / 2.0
                        print(f"[ECDIS] Repositioning ship to ENC center: {center_lat:.4f}, {center_lon:.4f}")
                        self.ship.lat = center_lat
                        self.ship.lon = center_lon
                else:
                    # No ship object passed; update internal defaults so draw() grid aligns
                    center_lat = (self.latN + self.latS) / 2.0
                    center_lon = (self.lonW + self.lonE) / 2.0
                    print(f"[ECDIS] No ship object; stored center now {center_lat:.4f},{center_lon:.4f}")
            self.chart_status = f"ENC: {os.path.basename(enc_path)}"
            return True
        
        except Exception as e:
            print(f"[ECDIS] Failed to load ENC: {e}")
            self.enc_layers = {}
            return False

    def draw_enc_layers(self):
        """
        Render loaded ENC vector layers onto the screen.
        
        Converts Shapely geometries to Pygame line sequences and draws them.
        """
        if not hasattr(self, 'enc_layers') or not self.enc_layers:
            return
        
        # Color map for different layer types (S-57 layer names)
        layer_colors = {
            'LNDARE': (120, 100, 80),      # Land area (brownish)
            'DEPCNT': (150, 180, 220),     # Depth contours (light blue)
            'SLCONS': (100, 170, 200),     # Shoreline (medium blue)
            'COALNE': (60, 140, 200),      # Coastline (brighter blue)
            'BOYLAT': (255, 220, 60),      # Lateral buoys (yellow)
            'LIGHTS': (255, 255, 160),     # Lights (bright yellow)
        }
        
        for layer_name, geometries in self.enc_layers.items():
            color = layer_colors.get(layer_name, (150, 150, 150))
            
            for geom in geometries:
                # Extract coordinates from Shapely geometry
                try:
                    if geom.geom_type == 'LineString':
                        coords = list(geom.coords)
                    elif geom.geom_type == 'LinearRing':
                        coords = list(geom.coords)
                    elif geom.geom_type == 'Polygon':
                        coords = list(geom.exterior.coords)
                    elif geom.geom_type == 'MultiLineString':
                        for line in geom.geoms:
                            coords = list(line.coords)
                            if len(coords) > 1:
                                pts = [self.ll_to_xy(lat, lon) for lon, lat in coords]
                                pg.draw.lines(self.screen, color, False, pts, 1)
                        continue
                    elif geom.geom_type == 'MultiPolygon':
                        for poly in geom.geoms:
                            coords = list(poly.exterior.coords)
                            if len(coords) > 1:
                                pts = [self.ll_to_xy(lat, lon) for lon, lat in coords]
                                pg.draw.polygon(self.screen, color, pts, 1)
                        continue
                    else:
                        continue
                    
                    # Convert to screen coordinates and draw
                    if len(coords) > 1:
                        pts = [self.ll_to_xy(lat, lon) for lon, lat in coords]
                        if geom.geom_type == 'Polygon':
                            # Fill land polygons for visibility
                            width = 0 if layer_name == 'LNDARE' else 1
                            pg.draw.polygon(self.screen, color, pts, width)
                        else:
                            # Make coastlines slightly thicker
                            width = 2 if layer_name == 'COALNE' else 1
                            pg.draw.lines(self.screen, color, False, pts, width)
                
                except Exception as e:
                    # Skip geometries that can't be converted
                    pass

    def ll_to_xy(self, lat: float, lon: float) -> Tuple[int, int]:
        # Guard against degenerate bounds
        dx = (self.lonE - self.lonW) or 1e-9
        dy = (self.latN - self.latS) or 1e-9
        u = (lon - self.lonW) / dx
        v = (self.latN - lat) / dy
        x = self.view.left + int(u * self.view.width)
        y = self.view.top + int(v * self.view.height)
        return x, y

    def draw_grid(self, interval_deg=0.05):
        lat = self.latS
        while lat <= self.latN + 1e-6:
            x1, y1 = self.ll_to_xy(lat, self.lonW)
            x2, y2 = self.ll_to_xy(lat, self.lonE)
            pg.draw.line(self.screen, self.grid_color, (x1, y1), (x2, y2), 1)
            lab = self.font20.render(f"{lat:.2f}°N", True, self.text_color)
            self.screen.blit(lab, (self.view.left + 4, y1 - 10))
            lat += interval_deg
        lon = self.lonW
        while lon <= self.lonE + 1e-6:
            x1, y1 = self.ll_to_xy(self.latN, lon)
            x2, y2 = self.ll_to_xy(self.latS, lon)
            pg.draw.line(self.screen, self.grid_color, (x1, y1), (x2, y2), 1)
            lab = self.font20.render(f"{abs(lon):.2f}°{'W' if lon<0 else 'E'}", True, self.text_color)
            self.screen.blit(lab, (x1 + 3, self.view.top + 3))
            lon += interval_deg

    def draw(self, ship=None):
        """Render the chart and ship. If a Ship object is available use its
        live position to recenter the chart bounds each frame. """
        # Prefer explicit ship argument, fall back to stored reference
        current_ship = ship or self.ship

        # If follow mode is enabled, recenter the visible bounds around
        # the moving ship. Otherwise leave the bounds (from sidecar or
        # initial values) fixed so the ship can move across the chart.
        if current_ship is not None and self.follow_ship:
            margin = 0.4
            self.latN = current_ship.lat + margin
            self.latS = current_ship.lat - margin
            self.lonW = current_ship.lon - margin
            self.lonE = current_ship.lon + margin

        # One-time console debug so we can see whether a chart image was
        # present at runtime (helps diagnose 'only grid' symptoms).
        if not self._debug_log_shown:
            print(f"[ECDIS] draw(): chart_img={'Yes' if self.chart_img else 'No'} | status='{self.chart_status}' | bounds=({self.latN:.4f},{self.latS:.4f},{self.lonW:.4f},{self.lonE:.4f})")
            self._debug_log_shown = True

        pg.draw.rect(self.screen, self.water_bg, self.view)

        # Blit preloaded chart image if available
        if self.chart_img:
            # chart_img was scaled to view size at load time; blit at view.topleft
            self.screen.blit(self.chart_img, (self.view.left, self.view.top))
        else:
            # fallback schematic coastline
            pts = [self.ll_to_xy(lat, lon) for (lat, lon) in self.fallback_coast]
            if len(pts) > 1:
                pg.draw.lines(self.screen, self.land_color, False, pts, 2)

        # Draw ENC vector layers if loaded
        self.draw_enc_layers()

        # Grid and labels
        self.draw_grid(interval_deg=0.05)

        # Draw ship marker if we have coordinates
        if current_ship is not None:
            sx, sy = self.ll_to_xy(current_ship.lat, current_ship.lon)
            pg.draw.circle(self.screen, (255, 255, 0), (sx, sy), 5, 0)
            pg.draw.line(self.screen, (255,255,0), (sx, sy), (sx, sy - 14), 2)

        title = self.font28.render("Chart Training Aid — Strait of Gibraltar", True, self.text_color)
        self.screen.blit(title, (self.view.left + 10, self.view.top - 30))

        # Show chart status and current ship coords for debugging/visibility
        status_text = self.chart_status
        if current_ship is not None:
            status_text += f"  | Ship: {current_ship.lat:.4f}N, {current_ship.lon:.4f}"
        status = self.font20.render(status_text, True, self.text_color)
        self.screen.blit(status, (self.view.left + 10, self.view.bottom + 4))
