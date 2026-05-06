# Dev Log — Bridge Simulator

Date: 2025-11-18

## Project Overview
Pygame-based bridge/radar trainer with parallel web UIs. Desktop loop renders radar and ECDIS; web radar server streams state (radar/bridge/3D) and Leaflet ECDIS shows ship track. ENC loader (GDAL/Fiona/Shapely) supports professional charts and GeoJSON export. Target is IMO Model Courses 1.07/1.08 and STCW A-II/1, A-II/2 competencies, architected for future DNV Class B submission.

## Today’s Task Plan (10–20 items)
1) Refresh architecture blueprint (current vs target) in `ARCHITECTURE.md`.
2) Formalize dev log and task tracking in `DEVLOG.md`.
3) Identify module gaps and propose implementation order (ARPA, AIS, guard zones, trails).
4) Add scaffolding modules: ARPA tracker, guard zones, trails manager, AIS stub.
5) Integrate guard zone/trails hooks into radar display (non-breaking default).
6) Define config schema notes for validation/hot-reload.
7) Map radar processing chain (RM/TM, vectors, trails, alarms) for implementation.
8) Map ECDIS chart ingest/rendering enhancements (routes, waypoints, zoom/pan).
9) Review web radar server for ARPA/scene hooks; outline API additions.
10) Review ship motion model; plan turn-rate and wind/current influences.
11) Draft launcher/menu requirements (Start/Settings/Exit) and UI changes.
12) Outline test plan (unit for geo math, ARPA CPA/TCPA, web API).
13) Document performance goals and profiling checkpoints.
14) Set short roadmap for radar features (guard zone, trails, vectors, TX, alarms).
15) Set short roadmap for ECDIS features (route, planned track drift, sync).
16) Capture future DNV readiness notes (logging, determinism, traceability).
17) Update docs after code changes.

## TODO
- Add ARPA/TT target tracking with CPA/TCPA and alarms.
- Add AIS/AIS-like overlays (optional data source).
- Flesh out bridge controls model (rudder, engines, telegraph) feeding UI.
- Improve weather/sea state model affecting clutter/visuals.
- Add automated tests (geo math, DR integrator, APIs).
- Add config validation/schema and hot-reload support.
- Improve chart management (sample data fetcher, caching, error handling).
- Optimize web 3D demo data (land mesh caching, LOD).
- Implement guard zones and alarms in radar UI and web server.
- Implement trails (true/relative) with decay control.
- Implement launcher/menu polish with Start/Settings/Exit flow.

## Initial Implementation Order (short-term)
1) Wire guard zones/trails into radar rendering and web state; add alarms.
2) Integrate ARPA tracker with web radar targets; expose CPA/TCPA via API.
3) Add AIS overlay from simulator feed; harmonize with ARPA list.
4) Enhance Pygame radar UI with guard zone toggles, trails, vectors.
5) Improve ECDIS: pan/zoom, route/waypoints, synchronized ship.
6) Build launcher menu (Start/Settings/Exit) and settings persistence.
7) Add config validation/hot-reload path.
8) Add test harnesses for geo math, ARPA calculations, API contracts.

## Completed
- Created architecture document and updated with target blueprint.
- Created dev log with expanded plan and TODOs.
- Added scaffolding modules: ARPA tracker, guard zones, trails manager, AIS simulator.
- Wired radar display to maintain own-ship trail history (for future rendering).
- Added web ECDIS chart load guardrail (~150MB) to avoid accidental OOM while allowing large exports.
- Added ECDIS web viewer guardrail to skip loading oversized GeoJSON exports (>25MB) to avoid browser OOM.
