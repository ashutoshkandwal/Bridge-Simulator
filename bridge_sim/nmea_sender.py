"""NMEA 0183 output for feeding MARIS ECDIS900 over LAN.

This module sends the minimum own-ship navigation sentences that were proven to
work with MARIS Sensor Monitor network input:

- GPGGA: GPS fix, position, satellites, HDOP
- GPRMC: recommended minimum navigation data
- GPVTG: course and speed over ground
- HEHDT: true heading
- GPZDA: UTC date/time

Default transport is UDP because MARIS Network sensor accepted UDP on port 8011
in the live test.
"""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional


@dataclass
class NMEAConfig:
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8011
    protocol: str = "udp"
    rate_hz: float = 1.0


class NMEASender:
    """Small UDP/TCP NMEA sender for own-ship data."""

    def __init__(self, config: NMEAConfig):
        self.config = config
        self._last_send_time = 0.0
        self._sock: Optional[socket.socket] = None
        self._connected = False

        if self.config.enabled:
            self._open_socket()

    @classmethod
    def from_dict(cls, data: dict | None) -> "NMEASender":
        data = data or {}
        cfg = NMEAConfig(
            enabled=bool(data.get("enabled", False)),
            host=str(data.get("host", "127.0.0.1")),
            port=int(data.get("port", 8011)),
            protocol=str(data.get("protocol", "udp")).lower(),
            rate_hz=float(data.get("rate_hz", 1.0)),
        )
        return cls(cfg)

    def _open_socket(self) -> None:
        if self._sock is not None:
            return
        if self.config.protocol == "tcp":
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2.0)
            try:
                self._sock.connect((self.config.host, self.config.port))
                self._connected = True
            except OSError as exc:
                print(f"[NMEA] TCP connection failed: {exc}")
                self._connected = False
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._connected = True

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
        self._sock = None
        self._connected = False

    def send_ship(self, lat: float, lon: float, heading: float, speed_kn: float, cog: float | None = None, force: bool = False) -> bool:
        """Send own-ship position/heading/speed to MARIS.

        Args:
            lat: latitude in decimal degrees, north positive.
            lon: longitude in decimal degrees, east positive, west negative.
            heading: true heading in degrees.
            speed_kn: speed over ground in knots.
            cog: course over ground in degrees. If omitted, heading is used.
            force: if True, ignore rate limit and send immediately.
        """
        if not self.config.enabled:
            return False

        now = time.time()
        min_interval = 1.0 / max(0.1, self.config.rate_hz)
        if not force and now - self._last_send_time < min_interval:
            return False

        self._open_socket()
        if self._sock is None or not self._connected:
            return False

        cog_value = heading if cog is None else cog
        sentences = build_own_ship_sentences(
            lat=lat,
            lon=lon,
            heading=heading,
            speed_kn=speed_kn,
            cog=cog_value,
        )

        try:
            payload = "\r\n".join(sentences) + "\r\n"
            if self.config.protocol == "tcp":
                self._sock.sendall(payload.encode("ascii"))
            else:
                for sentence in sentences:
                    self._sock.sendto((sentence + "\r\n").encode("ascii"), (self.config.host, self.config.port))
            self._last_send_time = now
            return True
        except OSError as exc:
            print(f"[NMEA] Send failed: {exc}")
            if self.config.protocol == "tcp":
                self.close()
            return False


def checksum(sentence_body: str) -> str:
    csum = 0
    for char in sentence_body:
        csum ^= ord(char)
    return f"${sentence_body}*{csum:02X}"


def _format_lat(lat: float) -> tuple[str, str]:
    hemi = "N" if lat >= 0 else "S"
    value = abs(lat)
    degrees = int(value)
    minutes = (value - degrees) * 60.0
    return f"{degrees:02d}{minutes:06.3f}", hemi


def _format_lon(lon: float) -> tuple[str, str]:
    hemi = "E" if lon >= 0 else "W"
    value = abs(lon)
    degrees = int(value)
    minutes = (value - degrees) * 60.0
    return f"{degrees:03d}{minutes:06.3f}", hemi


def build_own_ship_sentences(lat: float, lon: float, heading: float, speed_kn: float, cog: float) -> list[str]:
    """Build MARIS-friendly own ship NMEA sentences with valid checksums."""
    now = datetime.now(timezone.utc)
    utc_time = now.strftime("%H%M%S")
    utc_date = now.strftime("%d%m%y")

    lat_text, lat_hemi = _format_lat(lat)
    lon_text, lon_hemi = _format_lon(lon)
    heading = heading % 360.0
    cog = cog % 360.0
    speed_kn = max(0.0, float(speed_kn))

    gga = checksum(
        f"GPGGA,{utc_time},{lat_text},{lat_hemi},{lon_text},{lon_hemi},1,08,1.0,10.0,M,0.0,M,,"
    )
    rmc = checksum(
        f"GPRMC,{utc_time},A,{lat_text},{lat_hemi},{lon_text},{lon_hemi},{speed_kn:.1f},{cog:.1f},{utc_date},,,A"
    )
    vtg = checksum(
        f"GPVTG,{cog:.1f},T,,M,{speed_kn:.1f},N,{speed_kn * 1.852:.1f},K,A"
    )
    hdt = checksum(f"HEHDT,{heading:.1f},T")
    zda = checksum(f"GPZDA,{utc_time},{now.day:02d},{now.month:02d},{now.year},00,00")

    return [gga, rmc, vtg, hdt, zda]


def demo_moving_ship(host: str, port: int = 8011) -> None:
    """Standalone test: ship entering English Channel from west."""
    sender = NMEASender(NMEAConfig(enabled=True, host=host, port=port, protocol="udp", rate_hz=1.0))
    lat = 49.500000
    lon = -6.000000
    heading = 80.0
    speed = 12.0

    print(f"[NMEA DEMO] Sending to {host}:{port}. Press Ctrl+C to stop.")
    while True:
        sender.send_ship(lat, lon, heading, speed, cog=heading, force=True)
        print(f"LAT={lat:.6f}, LON={lon:.6f}, HDG={heading:.1f}, SPD={speed:.1f}")
        # Simple approximate movement for one second at current course/speed.
        distance_nm = speed / 3600.0
        import math
        lat += (distance_nm / 60.0) * math.cos(math.radians(heading))
        lon += (distance_nm / 60.0) * math.sin(math.radians(heading)) / max(1e-6, math.cos(math.radians(lat)))
        time.sleep(1.0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send demo NMEA own-ship data to MARIS ECDIS.")
    parser.add_argument("host", help="MARIS ECDIS computer IP address")
    parser.add_argument("--port", type=int, default=8011, help="MARIS network sensor port")
    args = parser.parse_args()
    demo_moving_ship(args.host, args.port)
