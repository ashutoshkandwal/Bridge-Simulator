"""Smoke checks for Codespaces/GitHub Actions.

This test verifies that the repository has the basic package structure needed by
main.py. It does not open a Pygame window or start the simulator.
"""

from __future__ import annotations

import importlib
from pathlib import Path

REQUIRED_PATHS = [
    "main.py",
    "requirements.txt",
    "config.json",
    "bridge_sim/__init__.py",
    "bridge_sim/radar.py",
    "bridge_sim/ecdis.py",
    "bridge_sim/controls.py",
    "bridge_sim/models.py",
    "bridge_sim/utils.py",
    "bridge_sim/web_ecdis.py",
    "bridge_sim/web_radar.py",
    "web/server.py",
    "web/radar_server.py",
]

REQUIRED_IMPORTS = [
    "bridge_sim",
    "bridge_sim.utils",
    "bridge_sim.models",
    "bridge_sim.controls",
    "bridge_sim.radar",
    "bridge_sim.ecdis",
    "bridge_sim.web_ecdis",
    "bridge_sim.web_radar",
    "main",
]


def test_required_paths_exist() -> None:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    assert not missing, f"Missing required project files: {missing}"


def test_required_imports() -> None:
    failures = []
    for module_name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - failure detail is useful here
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")
    assert not failures, "Import failures:\n" + "\n".join(failures)


if __name__ == "__main__":
    test_required_paths_exist()
    test_required_imports()
    print("Smoke import check passed.")
