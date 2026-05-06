# Bridge Simulator — Architecture

Status: extended blueprint (updated after deep scan)

## Overview
Python/Pygame bridge simulator with desktop radar/ECDIS views plus parallel web UIs (radar viewer, bridge controls, 3D bridge demo, Leaflet ECDIS). ENC vector data can be loaded via GDAL/Fiona/Shapely and exported to GeoJSON for web clients. Configuration is driven by `config.json`; scenarios persist to `last_scenario.json`. This document captures the current system and the target professional architecture ready to satisfy IMO Model Courses (1.07/1.08), STCW A-II/1, A-II/2 competencies, and to stage for later DNV class approval.

## Module Map (current)
- `bridge_sim/main.py` — app entry/state machine (menu → radar → ecdis → controls), spins up web servers (radar port 5001, ECDIS port 5000), pushes ship/targets/wind to web layers, headless mode keeps servers alive.
- `bridge_sim/radar.py` — Pygame radar PPI rendering, range/motion (RM/TM), course/north-up, UI widgets via `ui.py` + `panel.py`, pulls config-driven layout/colors, handles sea clutter, integrates with web radar for targets.
- `bridge_sim/ecdis.py` — Pygame ECDIS: loads raster charts or fallback coastline; can overlay ENC layers when loaded; geospatial transforms lat/lon → screen.
- `bridge_sim/controls.py` — placeholder control logic (ships/bridge controls to expand).
- `bridge_sim/models.py` — core data classes (`Ship`, `Target`, etc.), position update math.
- `bridge_sim/utils.py` — config loading, scenario persistence helpers.
- `bridge_sim/web_radar.py` — helper to start/coordinate `web/radar_server.py`.
- `bridge_sim/web_ecdis.py` — helper to start/coordinate `web/server.py` (Leaflet ECDIS).
- `bridge_sim/panel.py`, `bridge_sim/ui.py` — radar UI components and panels.
- `bridge_sim/arpa.py` — ARPA tracker scaffold with CPA/TCPA calculations.
- `bridge_sim/guard_zone.py` — guard zone definitions and intrusion checks.
- `bridge_sim/trails.py` — trail manager for true/relative trails.
- `bridge_sim/ais.py` — simulated AIS contact generator (stub for future feed).
- `bridge_sim/areas/` — charts (raster + metadata, ENC files under `noaa_charts/`).
- `tools/noaa_enc_loader.py` — GDAL/Fiona/Shapely-based ENC loader/exporter.
- `tools/*.py` — utilities to extract/export charts, diagnostics.
- `web/` — Flask apps and static UIs:
  - `web/radar_server.py` — REST/WebSocket radar+bridge server, DR integrator, scene API, land mesh API, command handling.
  - `web/server.py` — Leaflet ECDIS server with WebSocket ship updates.
  - `web/index.html`, `web/radar_viewer.html`, `web/bridge_controls.html`, `web/bridge3d_demo.html` — browser UIs.
  - `web/static/` — bundled assets (Leaflet, images, CSS/JS).

## Data Flow (text diagrams)

Desktop loop (Pygame):
```
Menu inputs → Ship/targets/wind (bridge_sim.main)
    ↓
RadarDisplay.update/draw (pygame) → local rendering
    ↓ push
web_radar.push_radar_update → web/radar_server.py (state)
    ↓ broadcast
Web radar viewer / bridge controls / 3D demo (WS/REST)

Ship state → ECDISDisplay.draw (pygame)
    ↓ push
web_ecdis.update_ship → web/server.py → Leaflet viewer WS
```

ENC ingestion/export:
```
ENC (.000/.gpkg) → tools.noaa_enc_loader.ENChart
    → in-app overlay (bridge_sim.ecdis.load_noaa_enc)
    → export chart_export.geojson (for web/radar land, 3D mesh, etc.)
```

True/Relative Motion (web radar background integrator):
```
radar_state {lat, lon, hdg, spd, mode/motion, targets} --(DR loop)--> updated ship/targets (x,y,lat,lon)
    --(broadcast)--> browsers
    --(bridge_sim.web_ecdis)--> ECDIS viewer ship updates
```

## Config & Persistence
- `config.json` — radar ranges, PPI size, colors, UI layout.
- `last_scenario.json` — last menu inputs.
- `chart_export.geojson` — exported ENC features for web (land mesh, echoes).

## Target Professional Architecture (blueprint)
- Core simulation layer
  - `SimClock`: fixed/variable timestep management, pause/slow/fast support.
  - `WorldState`: canonical ship state (lat, lon, sog, cog, heading, turn rate, drift/current, wind), targets, AIS contacts, alarms.
  - `Physics`: integrates ship kinematics (SOG/COG/heading/turn rate) and environmental effects (wind/current) with earth model (WGS84 great-circle approximations).
- Sensor/processing layer
  - `RadarSensor`: abstraction for PPI settings (range scales, TM/RM, north-up/course-up/head-up, stabilization), generates detections with noise/clutter models.
  - `ARPAProcessor`: acquisition/track management, Kalman/α-β filtering, target association, vector prediction, CPA/TCPA, guard/limit alarms.
  - `AISFeed`: simulated AIS contacts with MMSI/type, course/speed/rot, quality flags; merges into radar overlay.
  - `TrailsManager`: true/relative trails with decay; motion vectors rendering.
  - `GuardZones`: sector/ring definitions, alarm hooks.
  - `ChartOverlay`: ENC/raster ingest, projection to screen, safety contour highlighting.
- Presentation layer
  - Desktop (Pygame): `RadarDisplay`, `ECDISDisplay`, `ControlsDisplay`, launcher menu; modular UI widgets (buttons, sliders, status blocks), configurable layout/themes; efficient surface caching.
  - Web: `RadarServer` (Flask/WS), `ECDISServer` (Leaflet), `Bridge3D` (Three.js scene), all consuming the same `WorldState` via a pub/sub bridge.
  - UI framework: common widget primitives (button/slider/toggle/list), mode gating (menu vs radar vs ecdis), keyboard shortcuts, focus handling.
- Configuration & assets
  - `config.json` / `config.py` schema with validation, defaults, hot-reload.
  - Scenario definitions (traffic, env, chart set) load/save.
  - Chart manager: handles ENC set, raster packs, caches, exports.
- Telemetry & logging
  - Event logger (alarms, mode changes, inputs) with replay option.
  - Diagnostics overlay (FPS, timing, GC, dropped frames).
- Packaging
  - CLI launcher, service runners for web-only mode, self-check scripts.

## Radar Pipeline (target state)
1. Operator settings → RadarSensor config (range, gain, sea/rain clutter, mode TM/RM, stabilization, offset, trails, guard zones).
2. WorldState + env → radar detection model (applies clutter/noise, antenna sweep clock).
3. ARPAProcessor receives detections → association to existing tracks → filter update (α-β/Kalman) → kinematic prediction.
4. CPA/TCPA, guard zone, lost target alarms emitted → UI + log.
5. TrailsManager maintains decay buffers for true/relative trails.
6. Renderer overlays: ship symbol, heading/north marker, range rings, EBL/VRM, vectors/trails, guard zone arcs, AIS symbols, chart overlay if enabled.

## ARPA Processing Chain (target)
```
Raw detections (range, bearing, snr, time)
  -> CFAR/threshold (optional)
  -> Plot extractor (centroid)
  -> Plot-to-track association (NN/GNN, gating by range/bearing/vel)
  -> Track filter (α-β or Kalman, model CV/CT)
  -> Track maintenance (init, confirm, coast, drop)
  -> CPA/TCPA computation vs ownship vector
  -> Alarm checks (CPA/TCPA thresholds, guard zone, lost target)
  -> Outputs: track list with quality flags + vectors + trails
```

## Chart System Design (target)
- ENC loader: GDAL/Fiona/Shapely parses S-57/S-101, extracts key layers (LNDARE, COALNE, DEPCNT, BUOYS, LIGHTS, SLCONS, soundings) with styling config.
- Raster charts: georeferenced PNG/JPG + metadata.
- Projection: WGS84 to local ENU or simple equirectangular for small areas; consistent transform shared by radar/ECDIS/web viewers.
- Exports: GeoJSON/tiles for web clients; land mesh generation for 3D demo.
- Safety layer: safety contour/depth shading, visible/invisible sector masks.

## UI Framework (target)
- Widget primitives with focus, keyboard, mouse, and mode gating.
- Layout via config (positions, sizes, colors, ranges).
- Status blocks for alarms, ARPA list, AIS list, environmental readouts.
- Controls panel for gain/sea/rain, guard zone setup, trails, vectors, TX, mode.

## Event Loop Structure (target)
- Main loop: process input → update simulation (physics) → update sensors/processors (radar/ARPA/AIS/trails/guard zones) → render (desktop) → broadcast (web) → sleep.
- Deterministic clock with accumulator to avoid frame-time coupling; rendering decoupled from physics tick where possible.

## Identified Gaps / Suggested Modules
- ARPA/TT tracking module (target acquisition, CPA/TCPA, alarms) — add `bridge_sim/arpa.py`.
- AIS overlay provider (simulated feed, later NMEA) — add `bridge_sim/ais.py`.
- Guard zone manager and alarms — add `bridge_sim/guard_zone.py`.
- Trails manager (true/relative) — add `bridge_sim/trails.py`.
- Control surfaces/engine model (rudder, RPM, telegraph) feeding bridge controls UI.
- Weather/sea state model influencing clutter and visuals.
- Logging/analytics module for scenarios and events.
- Config schema/validation and hot-reload.
- Automated tests (unit/integration for math, data flow, APIs).
- Packaging/CLI launcher script for headless vs GUI.
- Assets pipeline (chart management, cache, sample data fetcher).

## External Dependencies
- Runtime: pygame, flask, flask-cors, flask-sock.
- Optional ENC: gdal, fiona, shapely, pyproj (see `requirements.txt` and GDAL docs).

## Web Endpoints (radar_server highlights)
- `GET /` → index menu; `/radar` viewer; `/bridge3d` 3D demo; `/bridge_controls` UI.
- `GET /api/radar`, `/api/scene`, `/api/land_mesh`, `/api/chart_features` — state and chart-derived data.
- `POST /api/set_ship`, `/api/init_simulation` — update/init state.
- WS `/radar`, `/bridge` — live pushes.

## Build/Run Modes
- Desktop: `python -m bridge_sim.main` (window) or `--headless` to run servers only.
- Web servers auto-start from `main.py`; can also run `python web/radar_server.py` or `python web/server.py`.

## Future Architecture Notes
- Consider separating simulation core (physics/state) from renderers (pygame, web) behind a pub/sub state bus.
- Extract common geo/nav math into a utility module with tests.
- Introduce a plugin registry for sensors (radar, ecdis, ais) and outputs (web, desktop).
