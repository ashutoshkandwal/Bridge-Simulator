# Ship Setup Menu Implementation

## Changes Made

### 1. **main.py** - Ship Initialization Menu
- **Added menu input system** with four text input fields:
  - Latitude (°N)
  - Longitude (°W)
  - Heading (°T)
  - Speed (kn)

- **New attributes**:
  - `ship_lat`, `ship_lon`, `ship_heading`, `ship_speed` - stored initialization values
  - `input_fields` - dictionary tracking each input field state (value, active, rect)
  - `menu_ready` - flag to only advance when inputs are valid

- **New methods**:
  - `_handle_menu_input(events)` - processes keyboard and mouse input on the menu
  - Updated `_draw_menu()` - displays setup form with input boxes
  - Updated `_cycle_state()` - initializes Radar and ECDIS with the entered ship data

- **Input Handling**:
  - Click any field to edit
  - Type numbers, decimals, and minus signs
  - Press ENTER to move to next field
  - Press SPACE to validate and start (all fields must be valid floats)

### 2. **radar.py** - Accept Ship Parameter
- Modified `__init__` signature to accept optional `ship` parameter:
  ```python
  def __init__(self, screen: pg.Surface, cfg, ship: "Ship" = None)
  ```
- If no ship provided, creates default ship (backward compatible)
- If ship provided, uses it directly (from menu input)

### 3. **ecdis.py** - Center Chart on Ship Position
- Modified `__init__` signature to accept `ship_lat` and `ship_lon`:
  ```python
  def __init__(self, screen: pg.Surface, ship_lat: float = 36.15, ship_lon: float = -5.50)
  ```
- Chart bounds now center around the ship's starting position
- Margin of ±0.4° around ship for chart view

## Workflow

1. **Start the app** → displays SHIP SETUP menu
2. **Enter values**:
   - Click field → type value → press ENTER (or click next field)
   - Repeat for all 4 fields
3. **Press SPACE** → validates all inputs
4. **If valid** → creates Ship, Radar, and ECDIS with your parameters
   - Radar display shows ship at specified heading/speed/position
   - ECDIS chart centers on your ship's lat/lon
5. **Press SPACE again** → cycles to RADAR screen
6. **Use arrow keys** to adjust heading, EBL, VRM, etc.

## Default Values

If you don't change the inputs, defaults are:
- Latitude: 36.15°N
- Longitude: 5.50°W
- Heading: 45°T
- Speed: 24 knots

## Input Validation

- All fields must contain valid floating-point numbers
- Negative values allowed (for longitude in Western hemisphere)
- Invalid input prevents advancing (SPACE does nothing)
