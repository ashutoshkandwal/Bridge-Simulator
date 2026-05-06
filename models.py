
from collections import deque
import math
import pygame as pg

class Ship:
    def __init__(self, x, y, heading, speed, lat=20.0, lon=20.0):
        self.x = x
        self.y = y
        self.heading = heading
        self.speed = speed
        self.lat = lat
        self.lon = lon

    def update_position(self, dt, north, true_motion=False):
        # Geo position update based on heading and speed
        # Heading: 0°=North, 90°=East, 180°=South, 270°=West
        # Speed in knots, dt in seconds
        # 1 knot = 1 nautical mile per hour
        distance_nm = (self.speed * dt / 3600.0)  # distance traveled in NM
        
        # Convert heading to radians (0° = North, clockwise)
        heading_rad = math.radians(self.heading)
        
        # Update latitude (north/south): positive heading component goes north
        # cos(0°) = 1 (north), cos(180°) = -1 (south)
        self.lat += (distance_nm / 60.0) * math.cos(heading_rad)
        
        # Update longitude (east/west): positive heading component goes east
        # sin(90°) = 1 (east), sin(270°) = -1 (west)
        # Account for latitude convergence
        self.lon += (distance_nm / 60.0) * math.sin(heading_rad) / math.cos(math.radians(self.lat))

class Target:
    def __init__(self, ship: "Ship", nm_range, T_bearing, heading, speed, breadth=40, length=180):
        self.breadth = breadth
        self.length = length
        self.heading = heading
        self.speed = speed
        self.past_true: deque = deque(maxlen=100)
        self.past_rel: deque = deque(maxlen=100)
        self._init_from_rb(ship, nm_range, T_bearing)

    def _init_from_rb(self, ship: "Ship", nm_range, T_bearing):
        self.range = nm_range
        self.bearing = T_bearing
        self.x = ship.x + nm_range * math.sin(math.radians(T_bearing))
        self.y = ship.y - nm_range * math.cos(math.radians(T_bearing))
        self.aquire_window = pg.Rect(self.x - 50, self.y - 50, 100, 100)

    def update(self, dt, ship: "Ship", north, motion_mode: str, nm_to_px, spd_to_px_per_s):
        if motion_mode == 'TM':  # true motion
            self.x += spd_to_px_per_s(self.speed) * dt * math.sin(math.radians(self.heading - north))
            self.y -= spd_to_px_per_s(self.speed) * dt * math.cos(math.radians(self.heading - north))
        else:  # relative motion
            self.x += spd_to_px_per_s(self.speed) * dt * math.sin(math.radians(self.heading - north))
            self.y -= spd_to_px_per_s(self.speed) * dt * math.cos(math.radians(self.heading - north))
            self.x -= spd_to_px_per_s(ship.speed) * dt * math.sin(math.radians(ship.heading - north))
            self.y += spd_to_px_per_s(ship.speed) * dt * math.cos(math.radians(ship.heading - north))
        self.aquire_window = pg.Rect(self.x - 50, self.y - 50, 100, 100)
        # RB
        dx = self.x - ship.x
        dy = ship.y - self.y
        rng_px = math.hypot(dx, dy)
        rng_nm = rng_px / nm_to_px(1.0)
        bearing = (math.degrees(math.atan2(dx, dy)) + north) % 360
        self.range, self.bearing = rng_nm, bearing
