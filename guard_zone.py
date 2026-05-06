"""
Guard zone utilities for radar alarms.

Defines ring/sector guard zones and a manager to check target intrusions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class GuardZone:
    """Sector guard zone defined by inner/outer range (NM) and start/width bearing (deg)."""
    inner_nm: float
    outer_nm: float
    start_deg: float
    width_deg: float
    enabled: bool = True
    label: str = "GZ"

    def contains(self, range_nm: float, bearing_deg: float) -> bool:
        if not self.enabled:
            return False
        if range_nm < self.inner_nm or range_nm > self.outer_nm:
            return False
        # Normalize bearing and sector
        b = bearing_deg % 360.0
        start = self.start_deg % 360.0
        end = (start + self.width_deg) % 360.0
        if self.width_deg >= 360.0:
            return True
        if start <= end:
            return start <= b <= end
        # Wrap-around sector
        return b >= start or b <= end


class GuardZoneManager:
    def __init__(self):
        self.zones: List[GuardZone] = []

    def add_zone(self, zone: GuardZone):
        self.zones.append(zone)

    def clear(self):
        self.zones.clear()

    def check_targets(self, targets: Iterable[Dict]) -> List[Dict]:
        """
        Return list of target dicts that breach any enabled guard zone.
        Expects target dict keys: range (NM), bearing (deg).
        """
        hits: List[Dict] = []
        for tgt in targets:
            rng = float(tgt.get("range", tgt.get("range_nm", 0.0)))
            bearing = float(tgt.get("bearing", tgt.get("bearing_deg", 0.0)))
            for zone in self.zones:
                if zone.contains(rng, bearing):
                    hit = dict(tgt)
                    hit["guard_zone"] = zone.label
                    hits.append(hit)
                    break
        return hits
