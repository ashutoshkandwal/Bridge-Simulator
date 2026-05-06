# Area and chart data

Keep large chart datasets out of normal Git commits.

Recommended structure:

```text
bridge_sim/areas/
└── noaa_charts/
    ├── README.md
    └── local chart files (not committed)
```

The simulator can run without these files using fallback chart rendering. Add local ENC/chart files only on the training computer where required.
