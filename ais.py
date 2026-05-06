"""
Simulated AIS contact generator and data container.

Provides lightweight AIS contact objects and a deterministic generator
for demo purposes. Real-world feeds can later map NMEA/AIS binary
messages into the same structure.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass
class AISContact:
    mmsi: int
    lat: float
    lon: float
    sog: float
    cog: float
    heading: float
    nav_status: str = "under_way"
    vessel_type: str = "cargo"
    name: str = "AIS"
    last_update: float = time.time()

    def as_dict(self) -> Dict:
        return {
            "mmsi": self.mmsi,
            "lat": self.lat,
            "lon": self.lon,
            "sog": self.sog,
            "cog": self.cog,
            "heading": self.heading,
            "status": self.nav_status,
            "type": self.vessel_type,
            "name": self.name,
            "ts": self.last_update,
        }


class AISGenerator:
    """
    Simple deterministic AIS simulator around an ownship reference.
    Produces a handful of contacts with slow updates for demo overlays.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.contacts: Dict[int, AISContact] = {}
        self._next_mmsi = 123450000

    def _spawn_contact(self, lat: float, lon: float) -> AISContact:
        mmsi = self._next_mmsi
        self._next_mmsi += 1
        sog = 8 + self.rng.random() * 10
        cog = self.rng.random() * 360.0
        heading = cog
        name = f"SIM{mmsi % 1000:03d}"
        contact = AISContact(mmsi=mmsi, lat=lat, lon=lon, sog=sog, cog=cog, heading=heading, name=name)
        self.contacts[mmsi] = contact
        return contact

    def step(self, own_lat: float, own_lon: float, dt: float = 1.0, radius_nm: float = 6.0) -> List[AISContact]:
        """
        Advance AIS contacts around an ownship reference.
        Returns current list of contacts after motion update.
        """
        if not self.contacts:
            # Spawn 3 demo contacts distributed around ownship
            for ang in (30, 150, 270):
                dx_nm = radius_nm * math.sin(math.radians(ang))
                dy_nm = radius_nm * math.cos(math.radians(ang))
                lat = own_lat + dy_nm / 60.0
                lon = own_lon + dx_nm / (60.0 * max(0.1, math.cos(math.radians(own_lat))))
                self._spawn_contact(lat, lon)

        moved: List[AISContact] = []
        for c in self.contacts.values():
            distance_nm = c.sog * (dt / 3600.0)
            dy_nm = distance_nm * math.cos(math.radians(c.cog))
            dx_nm = distance_nm * math.sin(math.radians(c.cog))
            c.lat += dy_nm / 60.0
            c.lon += dx_nm / (60.0 * max(0.1, math.cos(math.radians(c.lat))))
            c.last_update = time.time()
            moved.append(c)
        return moved

    def as_dicts(self) -> List[Dict]:
        return [c.as_dict() for c in self.contacts.values()]
