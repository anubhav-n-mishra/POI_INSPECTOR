"""Geographic utility functions for coordinate transformations and calculations."""
import math
from typing import Tuple, List
from shapely.geometry import Polygon, Point, box
from shapely.ops import transform
import pyproj


def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
    """
    Convert latitude/longitude to tile coordinates at given zoom level.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        zoom: Zoom level (0-20)
    
    Returns:
        Tuple of (tile_x, tile_y)
    """
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (x, y)


def tile_to_lat_lon(x: int, y: int, zoom: int) -> Tuple[float, float]:
    """
    Convert tile coordinates to latitude/longitude.
    
    Args:
        x: Tile X coordinate
        y: Tile Y coordinate
        zoom: Zoom level
    
    Returns:
        Tuple of (latitude, longitude)
    """
    n = 2.0 ** zoom
    lon = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat = math.degrees(lat_rad)
    return (lat, lon)


def get_polygon_bounds(polygon: Polygon) -> Tuple[float, float, float, float]:
    """
    Get bounding box of a polygon.
    
    Args:
        polygon: Shapely Polygon
    
    Returns:
        Tuple of (min_lon, min_lat, max_lon, max_lat)
    """
    bounds = polygon.bounds
    return bounds  # (minx, miny, maxx, maxy)


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def polygon_to_meters(polygon: Polygon) -> Polygon:
    """
    Transform polygon from WGS84 (lat/lon) to Web Mercator (meters).
    
    Args:
        polygon: Polygon in WGS84 coordinates
    
    Returns:
        Polygon in Web Mercator projection
    """
    wgs84 = pyproj.CRS('EPSG:4326')
    web_mercator = pyproj.CRS('EPSG:3857')
    project = pyproj.Transformer.from_crs(wgs84, web_mercator, always_xy=True).transform
    return transform(project, polygon)


def polygon_from_meters(polygon: Polygon) -> Polygon:
    """
    Transform polygon from Web Mercator (meters) to WGS84 (lat/lon).
    
    Args:
        polygon: Polygon in Web Mercator projection
    
    Returns:
        Polygon in WGS84 coordinates
    """
    web_mercator = pyproj.CRS('EPSG:3857')
    wgs84 = pyproj.CRS('EPSG:4326')
    project = pyproj.Transformer.from_crs(web_mercator, wgs84, always_xy=True).transform
    return transform(project, polygon)


def expand_bounds(min_lon: float, min_lat: float, max_lon: float, max_lat: float, 
                  buffer_meters: float = 50) -> Tuple[float, float, float, float]:
    """
    Expand bounding box by a buffer distance.
    
    Args:
        min_lon, min_lat, max_lon, max_lat: Original bounds
        buffer_meters: Buffer distance in meters
    
    Returns:
        Expanded bounds tuple
    """
    # Approximate degrees per meter at this latitude
    center_lat = (min_lat + max_lat) / 2
    meters_per_degree_lat = 111320
    meters_per_degree_lon = 111320 * math.cos(math.radians(center_lat))
    
    buffer_lat = buffer_meters / meters_per_degree_lat
    buffer_lon = buffer_meters / meters_per_degree_lon
    
    return (
        min_lon - buffer_lon,
        min_lat - buffer_lat,
        max_lon + buffer_lon,
        max_lat + buffer_lat
    )


def validate_geojson_polygon(geojson_coords: List) -> Polygon:
    """
    Validate and convert GeoJSON coordinates to Shapely Polygon.
    
    Args:
        geojson_coords: GeoJSON coordinate array
    
    Returns:
        Shapely Polygon
    
    Raises:
        ValueError: If coordinates are invalid
    """
    try:
        # GeoJSON format: [[[lon, lat], [lon, lat], ...]]
        if not geojson_coords or not geojson_coords[0]:
            raise ValueError("Empty coordinates")
        
        coords = geojson_coords[0]  # Exterior ring
        if len(coords) < 3:
            raise ValueError("Polygon must have at least 3 points")
        
        polygon = Polygon(coords)
        
        if not polygon.is_valid:
            raise ValueError("Invalid polygon geometry")
        
        return polygon
    except Exception as e:
        raise ValueError(f"Invalid GeoJSON polygon: {str(e)}")
