"""Test satellite tile fetching with debug output."""
import sys
sys.path.append('backend')

from shapely.geometry import Polygon
from backend.utils.geo_utils import lat_lon_to_tile, get_polygon_bounds, expand_bounds

# Test with Target Store coordinates from sample_poi.geojson
coords = [
    [-122.4194, 37.7749],
    [-122.4184, 37.7749],
    [-122.4184, 37.7739],
    [-122.4194, 37.7739],
    [-122.4194, 37.7749]
]

polygon = Polygon(coords)
print("Testing Tile Calculation")
print("=" * 50)

# Get bounds
min_lon, min_lat, max_lon, max_lat = get_polygon_bounds(polygon)
print(f"\nOriginal bounds:")
print(f"  Lat: {min_lat:.6f} to {max_lat:.6f}")
print(f"  Lon: {min_lon:.6f} to {max_lon:.6f}")

# Expand bounds
min_lon_exp, min_lat_exp, max_lon_exp, max_lat_exp = expand_bounds(
    min_lon, min_lat, max_lon, max_lat, 50
)
print(f"\nExpanded bounds (50m buffer):")
print(f"  Lat: {min_lat_exp:.6f} to {max_lat_exp:.6f}")
print(f"  Lon: {min_lon_exp:.6f} to {max_lon_exp:.6f}")

# Test different zoom levels
for zoom in [17, 18, 19]:
    print(f"\n--- Zoom level {zoom} ---")
    
    # Calculate tiles (FIXED)
    x_min, y_min = lat_lon_to_tile(max_lat_exp, min_lon_exp, zoom)
    x_max, y_max = lat_lon_to_tile(min_lat_exp, max_lon_exp, zoom)
    
    # Ensure min < max
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min
    
    print(f"Tile range:")
    print(f"  X: {x_min} to {x_max} (count: {x_max - x_min + 1})")
    print(f"  Y: {y_min} to {y_max} (count: {y_max - y_min + 1})")
    print(f"  Total tiles: {(x_max - x_min + 1) * (y_max - y_min + 1)}")
    
    # Check if valid
    if x_min > x_max or y_min > y_max:
        print("  ⚠️ ERROR: Invalid tile range!")
    else:
        print("  ✓ Valid tile range")
