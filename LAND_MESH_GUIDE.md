# Land Mesh 3D Integration Guide

## Overview
The land mesh system converts LNDARE (land area) polygons from the chart GeoJSON into 3D geometry for the browser-based bridge view.

## Architecture

### Backend (`radar_server.py`)
- **Endpoint**: `/api/land_mesh`
- **Function**: `get_land_mesh()` - Reads chart_export.geojson and triangulates LNDARE polygons
- **Helper**: `_process_polygon_to_mesh()` - Converts lat/lon polygons to metric coordinates and triangulates

### Frontend (`bridge3d_demo.html`)
- **Function**: `fetchLandMesh()` - Fetches mesh data from API once at startup
- **Function**: `buildLandMeshes()` - Creates Three.js BufferGeometry from triangulated data
- **Group**: `landGroup` - Contains all land mesh objects

## Coordinate System

### Lat/Lon → Metric Conversion
```javascript
X = lon * 111320 * cos(lat)  // meters east
Z = -lat * 110540            // meters north (negative for Three.js)
Y = 0                         // sea level
```

### Triangulation
- Currently uses **simple fan triangulation** from first vertex
- Works for convex polygons
- Complex polygons with holes require proper earcut algorithm (future enhancement)

## Usage

### Access the 3D View
1. Start the simulator: `python -m bridge_sim.main` or run task "Run Simulator"
2. Open web menu: http://localhost:5001/
3. Click "3D Bridge View" card
4. Land mesh loads automatically on page load

### API Endpoints
- **Scene data**: `GET /api/scene` (ship, targets, environment)
- **Land mesh**: `GET /api/land_mesh` (triangulated geometry)

### Controls (3D Demo)
- **BINOCULAR VIEW**: Toggle narrow FOV (20° vs 60°)
- **DAY / NIGHT**: Toggle lighting mode
- **RESET CAMERA**: Reset OrbitControls view
- **Mouse drag**: Orbit camera (temporary controls)

## Rendering Details

### Material
```javascript
MeshPhongMaterial {
  color: 0x4a7c59,      // Land green
  side: DoubleSide,      // Visible from both sides
  flatShading: true      // Angular polygon look
}
```

### Performance
- Land mesh loads **once** at startup (`landLoaded` flag)
- Static geometry (no per-frame updates)
- Current implementation: no LOD or culling (pending optimization)

## Current Limitations

1. **Fan triangulation**: Only handles convex polygons correctly
2. **No holes**: Inner rings (holes in land) are ignored
3. **No simplification**: Full polygon detail always rendered
4. **No culling**: All land meshes rendered regardless of visibility

## Next Steps (Roadmap)

1. **Proper earcut triangulation**: Handle concave polygons and holes
2. **Polygon simplification**: Douglas-Peucker algorithm for LOD
3. **Frustum culling**: Only render visible land segments
4. **Texture mapping**: Add terrain textures (grass, sand, rock)
5. **Elevation data**: Extrude land to realistic heights
6. **Dynamic streaming**: Load/unload land based on distance

## Testing

### Verify Land Mesh API
```powershell
# Fetch land mesh data (warning: large response)
Invoke-RestMethod -Uri http://localhost:5001/api/land_mesh | ConvertTo-Json -Depth 3
```

### Console Debugging
Open browser DevTools Console in 3D view:
```
[LAND MESH] Fetching...
[LAND MESH] Received N segments
[LAND MESH] Built N land meshes
```

## Integration with Motion Modes

### True Motion (TM)
- Ship moves relative to land (land remains stationary)
- Camera rotates with heading but land stays fixed in world space

### Relative Motion (RM)
- Ship fixed at center
- Land would need to counter-translate (future enhancement)
- Currently land is static in world coordinates

## File Locations
- **Server**: `web/radar_server.py` (lines 158-250)
- **Client**: `web/bridge3d_demo.html` (land mesh functions)
- **Menu**: `web/index.html` (3D Bridge View card)
- **Chart**: `chart_export.geojson` (LNDARE source data)
