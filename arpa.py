"""
ARPA tracking scaffold.

Provides a lightweight tracker capable of maintaining target plots,
estimating relative motion, and computing CPA/TCPA. This is designed
to be extended with proper plot-to-track association and filtering.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class ARPATrack:
    track_id: int
    bearing_deg: float
    range_nm: float
    course_deg: float
    speed_kn: float
    last_update: float
    state: str = "acquired"  # acquired|tracking|coasting|lost
    cpa_nm: Optional[float] = None
    tcpa_min: Optional[float] = None
    quality: float = 1.0
    source_id: Optional[str] = None  # radar/ais/source tag
    age_s: float = 0.0

    def as_dict(self) -> Dict:
        return {
            "id": self.track_id,
            "bearing": self.bearing_deg,
            "range": self.range_nm,
            "course": self.course_deg,
            "speed": self.speed_kn,
            "cpa_nm": self.cpa_nm,
            "tcpa_min": self.tcpa_min,
            "state": self.state,
            "quality": self.quality,
            "age_s": self.age_s,
            "source": self.source_id,
        }


def _polar_to_xy(range_nm: float, bearing_deg: float) -> Tuple[float, float]:
    """Convert polar (range nm, bearing deg true) to local XY in NM (x east, y north)."""
    ang = math.radians(bearing_deg)
    return range_nm * math.sin(ang), range_nm * math.cos(ang)


def _relative_velocity(own_spd_kn: float, own_hdg_deg: float, tgt_spd_kn: float, tgt_crs_deg: float) -> Tuple[float, float]:
    """Return relative velocity components (target - own) in NM/s."""
    def comp(spd_kn: float, deg: float) -> Tuple[float, float]:
        ang = math.radians(deg)
        vx = (spd_kn / 3600.0) * math.sin(ang)
        vy = (spd_kn / 3600.0) * math.cos(ang)
        return vx, vy

    ovx, ovy = comp(own_spd_kn, own_hdg_deg)
    tvx, tvy = comp(tgt_spd_kn, tgt_crs_deg)
    return tvx - ovx, tvy - ovy


def _cpa_tcpa(own_spd_kn: float, own_hdg_deg: float, tgt_spd_kn: float, tgt_crs_deg: float, tgt_x_nm: float, tgt_y_nm: float) -> Tuple[float, float]:
    """
    Compute CPA (NM) and TCPA (minutes) using linear relative motion.
    Returns (cpa_nm, tcpa_min). TCPA positive = future, negative = past.
    """
    rvx, rvy = _relative_velocity(own_spd_kn, own_hdg_deg, tgt_spd_kn, tgt_crs_deg)
    rel_speed_sq = rvx * rvx + rvy * rvy
    if rel_speed_sq < 1e-12:
        return math.hypot(tgt_x_nm, tgt_y_nm), float("inf")
    tcpa_hours = -((tgt_x_nm * rvx + tgt_y_nm * rvy) / rel_speed_sq)
    tcpa_min = tcpa_hours * 60.0
    cpa_x = tgt_x_nm + rvx * tcpa_hours * 3600.0
    cpa_y = tgt_y_nm + rvy * tcpa_hours * 3600.0
    cpa_nm = math.hypot(cpa_x, cpa_y)
    return cpa_nm, tcpa_min


class ARPATracker:
    """
    Minimal ARPA tracker scaffolding.
    - Maintains tracks by provided IDs (caller must supply stable ids).
    - Computes CPA/TCPA vs own ship.
    - Provides hooks for future association/filtering.
    """

    def __init__(self, cpa_alarm_nm: float = 1.0, tcpa_alarm_min: float = 12.0):
        self.tracks: Dict[int, ARPATrack] = {}
        self._next_id = 1
        self.cpa_alarm_nm = cpa_alarm_nm
        self.tcpa_alarm_min = tcpa_alarm_min

    def _alloc_id(self) -> int:
        tid = self._next_id
        self._next_id += 1
        return tid

    def update(self, own_heading_deg: float, own_speed_kn: float, detections: Iterable[Dict], timestamp: Optional[float] = None) -> List[ARPATrack]:
        """
        Update tracker with current detections.

        Args:
            own_heading_deg: own ship heading (deg true)
            own_speed_kn: own ship speed (kn)
            detections: iterable of dicts with keys:
                - bearing (deg), range (NM), course (deg), speed (kn), id (optional)
            timestamp: optional epoch seconds; defaults to time.time()

        Returns:
            List of ARPATrack objects after update.
        """
        now = timestamp or time.time()
        seen_ids = set()

        for det in detections:
            bearing = float(det.get("bearing", 0.0))
            rng = float(det.get("range", 0.0))
            course = float(det.get("course", 0.0))
            speed = float(det.get("speed", 0.0))
            src_id = det.get("id")
            if src_id is None:
                track_id = self._alloc_id()
            else:
                track_id = int(src_id)
            seen_ids.add(track_id)

            tx, ty = _polar_to_xy(rng, bearing)
            cpa, tcpa = _cpa_tcpa(own_speed_kn, own_heading_deg, speed, course, tx, ty)

            track = self.tracks.get(track_id)
            if track is None:
                track = ARPATrack(
                    track_id=track_id,
                    bearing_deg=bearing,
                    range_nm=rng,
                    course_deg=course,
                    speed_kn=speed,
                    last_update=now,
                    state="acquired",
                    source_id=det.get("source"),
                )
                self.tracks[track_id] = track
            else:
                track.bearing_deg = bearing
                track.range_nm = rng
                track.course_deg = course
                track.speed_kn = speed
                track.state = "tracking"
                track.last_update = now

            track.cpa_nm = cpa
            track.tcpa_min = tcpa
            track.age_s = max(0.0, now - track.last_update)
            track.quality = max(0.0, min(1.0, track.quality + 0.05))

        # Coast / drop stale tracks
        drop_ids = []
        for tid, track in self.tracks.items():
            if tid not in seen_ids:
                track.state = "coasting"
                track.quality *= 0.9
                track.age_s = max(0.0, now - track.last_update)
                if track.age_s > 60.0:
                    track.state = "lost"
                    drop_ids.append(tid)
        for tid in drop_ids:
            self.tracks.pop(tid, None)

        return list(self.tracks.values())

    def alarm_hits(self) -> List[ARPATrack]:
        """Return tracks breaching CPA/TCPA thresholds."""
        hits = []
        for trk in self.tracks.values():
            if trk.cpa_nm is None or trk.tcpa_min is None:
                continue
            if trk.cpa_nm <= self.cpa_alarm_nm and 0 <= trk.tcpa_min <= self.tcpa_alarm_min:
                hits.append(trk)
        return hits

    def as_dicts(self) -> List[Dict]:
        return [t.as_dict() for t in self.tracks.values()]
