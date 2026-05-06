# 🎯 QUICK START - Your Chart in 5 Minutes

## 📦 What You Have
```
✓ Bridge simulator with Radar display
✓ ECDIS screen ready for charts
✓ 459 MB Gibraltar Strait chart archive
✓ All tools to extract and display the chart
```

## 🚀 Three Steps to Success

### Step 1: Extract Chart (1-2 min)
```bash
cd bridge_sim_configurable
python extract_chart.py
```
✓ Extracts JPG images from your CAB archive  
✓ Places them in `bridge_sim/areas/` folder  
✓ ECDIS will find them automatically  

### Step 2: Run Simulator (1 min)
```bash
python -m bridge_sim.main
```
✓ Simulator starts with menu  
✓ Input fields ready for your data  

### Step 3: Enter Position & View Chart (2 min)
```
Menu appears with 4 fields:
├─ Latitude (°N):  36.15   (default)
├─ Longitude (°W): 5.50    (default)
├─ Heading (°T):   45      (default)
└─ Speed (kn):     24      (default)

Press SPACE to confirm
Press SPACE → Radar screen
Press SPACE → ECDIS screen ← Your chart displays here! 🗺️
```

## ✨ Result
```
ECDIS Display shows:
┌──────────────────────────────────────┐
│  Your Gibraltar chart image          │
│                                      │
│         ★ Your ship (yellow)         │
│         | Your heading (line)        │
│                                      │
│  [Lat/Lon grid overlay]              │
│                                      │
├──────────────────────────────────────┤
│ Loaded: gibraltar.jpg                │
└──────────────────────────────────────┘
```

## ⏱️ Timeline
```
Now:     python extract_chart.py          [1-2 min]
Then:    python -m bridge_sim.main        [1 min  ]
Then:    Enter position (use defaults)    [1 min  ]
Then:    See your chart!                  [2 min  ]
─────────────────────────────────────────────────────
Total:   ~5 minutes to success!
```

## 📋 Checklist
- [ ] Run: `python extract_chart.py`
- [ ] See: "✓ Copied gibraltar.jpg"
- [ ] Run: `python -m bridge_sim.main`
- [ ] See: Menu with input fields
- [ ] Enter: Position data (or use defaults)
- [ ] Press: SPACE twice
- [ ] See: Your chart in ECDIS! ✓

## 🆘 If Something Goes Wrong
- Chart not showing? → See `AREAS_GUIDE.md`
- Don't know where to start? → See `SETUP_CHART.md`
- Want more details? → See `INDEX.md`

## 🎉 That's It!
Your chart is now integrated with your simulator!

**Start now:** `python extract_chart.py`
