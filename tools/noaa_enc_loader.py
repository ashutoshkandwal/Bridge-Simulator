"""
NOAA ENC (Electronic Navigational Chart) Loader

Loads S-57/S-101 format charts and extracts vector layers for rendering.

Requirements:
    pip install gdal fiona shapely pyproj

Usage:
    from tools.noaa_enc_loader import ENChart
    
    chart = ENChart('path/to/chart.000')
    bbox = chart.get_bounds()
    coastline = chart.get_layer('LNDSRF')
    chart.export_to_geojson('output.geojson')

"""
import os
import json
from typing import List, Dict, Tuple, Optional

try:
    from osgeo import ogr
    # Opt-in to GDAL exceptions so failures raise instead of silent error codes
    try:
        ogr.UseExceptions()
    except Exception:
        pass
    GDAL_AVAILABLE = True
except ImportError:
    GDAL_AVAILABLE = False
    print("[WARN] GDAL not available. Install with: pip install gdal")

try:
    import fiona
    FIONA_AVAILABLE = True
except ImportError:
    FIONA_AVAILABLE = False
    print("[WARN] Fiona not available. Install with: pip install fiona")

try:
    from shapely.geometry import shape, mapping
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("[WARN] Shapely not available. Install with: pip install shapely")


class ENChart:
    """
    NOAA ENC Chart loader using GDAL/OGR.
    
    Supports S-57 (.000, .001, etc.) and S-101 (.gpkg) formats.
    """
    
    def __init__(self, path: str):
        """
        Initialize and open a NOAA ENC chart.
        
        Args:
            path: Path to .000 (S-57) or .gpkg (S-101) file
        """
        if not GDAL_AVAILABLE:
            raise ImportError("GDAL is required. Install with: pip install gdal")
        
        self.path = path
        self.ds = None
        self.layers = {}
        self.bounds = None
        
        self._open()
        self._index_layers()
        self._compute_bounds()
    
    def _open(self):
        """Open the chart file using GDAL."""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Chart file not found: {self.path}")
        
        self.ds = ogr.Open(self.path)
        if self.ds is None:
            raise ValueError(f"Failed to open chart: {self.path}. Ensure GDAL supports S-57/S-101.")
        
        print(f"[ENC] Opened: {os.path.basename(self.path)}")
        print(f"[ENC] Layers available: {self.ds.GetLayerCount()}")
    
    def _index_layers(self):
        """Index all available layers by name and code."""
        for i in range(self.ds.GetLayerCount()):
            layer = self.ds.GetLayerByIndex(i)
            layer_name = layer.GetName()
            self.layers[layer_name] = layer
            print(f"[ENC] Layer {i}: {layer_name} ({layer.GetFeatureCount()} features)")
    
    def _compute_bounds(self):
        """Compute the overall bounding box in lat/lon."""
        if not self.layers:
            self.bounds = (90, -90, -180, 180)  # Default world bounds
            return
        
        # Prefer official coverage layer if present
        covr = self.layers.get('M_COVR')
        if covr is not None:
            try:
                min_lat, max_lat = 90.0, -90.0
                min_lon, max_lon = 180.0, -180.0
                covr.ResetReading()
                for f in covr:
                    g = f.GetGeometryRef()
                    if not g:
                        continue
                    e = g.GetEnvelope()  # (minx, maxx, miny, maxy)
                    if not e:
                        continue
                    minx, maxx, miny, maxy = e
                    min_lon = min(min_lon, float(minx))
                    max_lon = max(max_lon, float(maxx))
                    min_lat = min(min_lat, float(miny))
                    max_lat = max(max_lat, float(maxy))
                if min_lon < max_lon and min_lat < max_lat:
                    self.bounds = (max_lat, min_lat, min_lon, max_lon)
                    print(f"[ENC] Bounds (M_COVR): lat={self.bounds[1]:.5f}..{self.bounds[0]:.5f}, lon={self.bounds[2]:.5f}..{self.bounds[3]:.5f}")
                    return
            except Exception:
                pass

        min_lat, max_lat = 90.0, -90.0
        min_lon, max_lon = 180.0, -180.0

        def _valid_extent(ext):
            if ext is None:
                return False
            try:
                minx, maxx, miny, maxy = ext
            except Exception:
                return False
            # Ignore empty or degenerate extents (common for metadata-only layers)
            if minx == maxx or miny == maxy:
                return False
            # Ignore obvious junk extents
            if not (-360 <= minx <= 360 and -360 <= maxx <= 360 and -180 <= miny <= 180 and -180 <= maxy <= 180):
                return False
            # Some drivers return (0,0,0,0) for non-spatial layers
            if minx == 0 and maxx == 0 and miny == 0 and maxy == 0:
                return False
            return True

        for name, layer in self.layers.items():
            try:
                extent = layer.GetExtent()
            except Exception:
                extent = None
            if not _valid_extent(extent):
                continue
            minx, maxx, miny, maxy = extent
            min_lon = min(min_lon, float(minx))
            max_lon = max(max_lon, float(maxx))
            min_lat = min(min_lat, float(miny))
            max_lat = max(max_lat, float(maxy))

        # Fallback: use coverage layer M_COVR if global scan failed
        if (min_lon > max_lon) or (min_lat > max_lat) or (min_lon == 180.0 and max_lon == -180.0):
            covr = self.layers.get('M_COVR')
            if covr is not None:
                try:
                    covr.ResetReading()
                    for f in covr:
                        g = f.GetGeometryRef()
                        if not g:
                            continue
                        e = g.GetEnvelope()  # (minx, maxx, miny, maxy)
                        if e:
                            minx, maxx, miny, maxy = e
                            min_lon = min(min_lon, float(minx))
                            max_lon = max(max_lon, float(maxx))
                            min_lat = min(min_lat, float(miny))
                            max_lat = max(max_lat, float(maxy))
                except Exception:
                    pass

        # Clamp to plausible ranges and ensure ordering
        min_lon = max(-180.0, min_lon)
        max_lon = min(180.0, max_lon)
        min_lat = max(-90.0, min_lat)
        max_lat = min(90.0, max_lat)

        if min_lon > max_lon or min_lat > max_lat:
            # As a last resort, pick a tiny box around (0,0) to avoid crashes
            self.bounds = (0.1, -0.1, -0.1, 0.1)
        else:
            # Return as (latN, latS, lonW, lonE)
            self.bounds = (max_lat, min_lat, min_lon, max_lon)

        print(f"[ENC] Bounds: lat={self.bounds[1]:.5f}..{self.bounds[0]:.5f}, lon={self.bounds[2]:.5f}..{self.bounds[3]:.5f}")
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        Get chart bounding box.
        
        Returns:
            Tuple of (latN, latS, lonW, lonE) in degrees
        """
        return self.bounds
    
    def get_layer(self, layer_name: str):
        """
        Get all geometries in a layer.
        
        Args:
            layer_name: Layer name or code (e.g., 'LNDSRF' for land surfaces)
        
        Returns:
            List of Shapely geometry objects
        """
        if not SHAPELY_AVAILABLE:
            raise ImportError("Shapely is required. Install with: pip install shapely")
        
        if layer_name not in self.layers:
            raise KeyError(f"Layer not found: {layer_name}. Available: {list(self.layers.keys())}")
        
        layer = self.layers[layer_name]
        layer.ResetReading()
        
        geometries = []
        for feature in layer:
            geom = feature.GetGeometryRef()
            if geom:
                wkt = geom.ExportToWkt()
                geom_obj = shape(json.loads(ogr.Geometry(wkt=wkt).ExportToJson()))
                geometries.append(geom_obj)
        
        print(f"[ENC] Extracted {len(geometries)} geometries from layer '{layer_name}'")
        return geometries
    
    def get_features_with_attributes(self, layer: str) -> List[Dict]:
        """
        Get features including their attributes and geometries.
        
        Args:
            layer: Layer name or code
        
        Returns:
            List of feature dictionaries with 'geometry' and 'properties'
        """
        if layer not in self.layers:
            raise KeyError(f"Layer not found: {layer}")
        
        layer_obj = self.layers[layer]
        layer_obj.ResetReading()
        
        features = []
        for ogr_feature in layer_obj:
            geom = ogr_feature.GetGeometryRef()
            if geom:
                geom_json = json.loads(geom.ExportToJson())
                
                # Extract attributes
                attributes = {}
                for field_index in range(ogr_feature.GetFieldCount()):
                    field_def = ogr_feature.GetFieldDefnRef(field_index)
                    field_name = field_def.GetName()
                    field_value = ogr_feature.GetField(field_index)
                    attributes[field_name] = field_value
                
                features.append({
                    'geometry': geom_json,
                    'properties': attributes
                })
        
        return features
    
    def export_to_geojson(self, output_path: str, layers: Optional[List[str]] = None):
        """
        Export one or more layers to GeoJSON format.
        
        Args:
            output_path: Output file path (.geojson)
            layers: List of layer names to export (default: all)
        """
        if layers is None:
            layers = list(self.layers.keys())
        
        geojson = {
            'type': 'FeatureCollection',
            'features': []
        }
        
        for layer_name in layers:
            if layer_name not in self.layers:
                print(f"[WARN] Layer not found: {layer_name}")
                continue
            
            features = self.get_features_with_attributes(layer_name)
            for feat in features:
                geojson['features'].append({
                    'type': 'Feature',
                    'geometry': feat['geometry'],
                    'properties': {
                        'layer': layer_name,
                        **feat['properties']
                    }
                })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2)
        
        print(f"[ENC] Exported {len(geojson['features'])} features to {output_path}")
    
    def export_to_shapefile(self, output_dir: str, layers: Optional[List[str]] = None):
        """
        Export one or more layers to Shapefile format.
        
        Requires fiona and shapely.
        
        Args:
            output_dir: Output directory
            layers: List of layer names to export (default: all)
        """
        if not FIONA_AVAILABLE or not SHAPELY_AVAILABLE:
            raise ImportError("Fiona and Shapely required. Install with: pip install fiona shapely")
        
        if layers is None:
            layers = list(self.layers.keys())
        
        os.makedirs(output_dir, exist_ok=True)
        
        for layer_name in layers:
            if layer_name not in self.layers:
                print(f"[WARN] Layer not found: {layer_name}")
                continue
            
            features = self.get_features_with_attributes(layer_name)
            if not features:
                continue
            
            # Determine geometry type from first feature
            first_geom = features[0]['geometry']
            geom_type = first_geom.get('type', 'Point')
            
            # Schema for fiona
            schema = {
                'geometry': geom_type,
                'properties': {'layer': 'str'}
            }
            
            output_path = os.path.join(output_dir, f'{layer_name}.shp')
            with fiona.open(
                output_path, 'w',
                driver='ESRI Shapefile',
                schema=schema,
                crs='EPSG:4326'
            ) as dst:
                for feat in features:
                    dst.write({
                        'type': 'Feature',
                        'geometry': feat['geometry'],
                        'properties': {'layer': layer_name}
                    })
            
            print(f"[ENC] Exported {len(features)} features from '{layer_name}' to {output_path}")


def main():
    """Test the ENChart loader with a sample file."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tools/noaa_enc_loader.py <path_to_chart.000>")
        print("\nExample: python tools/noaa_enc_loader.py bridge_sim/areas/noaa_charts/US5VA18M.000")
        return 1
    
    chart_path = sys.argv[1]
    
    try:
        chart = ENChart(chart_path)
        
        bounds = chart.get_bounds()
        print(f"\nChart bounds: {bounds}")
        
        # List available layers
        print(f"\nAvailable layers: {list(chart.layers.keys())}")
        
        # Extract a sample layer
        if 'LNDSRF' in chart.layers:
            print("\nExtracting LNDSRF (Land Surfaces)...")
            coastline = chart.get_layer('LNDSRF')
            print(f"  Got {len(coastline)} geometries")
        
        # Export to GeoJSON
        print("\nExporting to GeoJSON...")
        chart.export_to_geojson('chart_export.geojson')
        
        print("\n✓ ENC chart loaded and exported successfully!")
        return 0
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 2


if __name__ == '__main__':
    import sys
    raise SystemExit(main())
