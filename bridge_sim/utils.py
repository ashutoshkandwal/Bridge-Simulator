"""Utility helpers for the Bridge Simulator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.json"
LAST_SCENARIO_PATH = ROOT_DIR / "last_scenario.json"


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Return value limited to the inclusive range [minimum, maximum]."""
    return max(minimum, min(maximum, value))


def load_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load a JSON object from path. Return default/{} if unavailable or invalid."""
    if default is None:
        default = {}
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data if isinstance(data, dict) else default
    except Exception as exc:
        print(f"[UTILS] Could not load {path}: {exc}")
    return default


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Write a JSON object to path."""
    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
    except Exception as exc:
        print(f"[UTILS] Could not save {path}: {exc}")


def load_config() -> Dict[str, Any]:
    """Load config.json from the repository root."""
    return load_json(CONFIG_PATH, default={})


def load_last_scenario() -> Dict[str, Any]:
    """Load the last menu/scenario values, if present."""
    return load_json(LAST_SCENARIO_PATH, default={})


def save_last_scenario(data: Dict[str, Any]) -> None:
    """Persist the last menu/scenario values."""
    save_json(LAST_SCENARIO_PATH, data)
