# NOAA ENC chart files

Large ENC/chart files are intentionally not committed here.

Expected local path used by `main.py`:

```text
bridge_sim/areas/noaa_charts/US4MD20M.000
```

For GitHub, keep only this README placeholder. Put actual chart files on the local simulator computer.

If using image charts, place the image and a same-named JSON sidecar in `bridge_sim/areas/`, for example:

```text
bridge_sim/areas/english_channel.png
bridge_sim/areas/english_channel.json
```

Example JSON sidecar:

```json
{
  "latN": 50.5,
  "latS": 49.0,
  "lonW": -6.5,
  "lonE": -2.0
}
```
