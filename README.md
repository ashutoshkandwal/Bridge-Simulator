
# Bridge Simulator — Configurable (Pygame)

Edit **config.json** to tweak ranges, colors, and UI positions *without touching code*.

## config.json keys
- `ranges_nm`: ordered list of range steps NM (used by + / - buttons)
- `ppi_radius_px`: PPI circle radius in pixels
- `colors`: named UI colors (RGB arrays)
- `ui_positions`:
  - `right_panel`, `control_panel` as `[x,y,w,h]`
  - `buttons` dict: each `[x,y,w,h]`
  - `bars` dict: each `[x,y,w,h]`

## Run
```bash
pip install -r requirements.txt
python -m bridge_sim.main
```

## Tips
- Add or remove range steps freely (e.g., `[0.5, 1, 2, 4, 8, 16]`).
- Move any button/bar by changing its rectangle numbers.
- Change theme colors live after restart.
