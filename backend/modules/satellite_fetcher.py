"""Satellite imagery fetcher with support for multiple providers."""
import os
import math
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import requests
from io import BytesIO
import time

from config import settings
from utils.geo_utils import lat_lon_to_tile, get_polygon_bounds, expand_bounds
from shapely.geometry import Polygon


class SatelliteFetcher:
    """Fetches and processes satellite imagery for POI analysis."""
    
    def __init__(self):
        """Initialize satellite fetcher with configuration."""
        self.cache_dir = Path(settings.base_dir) / settings.image_cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.zoom = settings.zoom_level
        
        # Determine tile URL based on configuration
        if settings.use_mapbox and settings.mapbox_token:
            self.tile_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{self.zoom}/{{x}}/{{y}}?access_token={settings.mapbox_token}"
            print("✓ Using Mapbox satellite imagery")
        else:
            self.tile_url = settings.tile_url
            if "arcgisonline" in self.tile_url:
                print("✓ Using ESRI World Imagery (free, high-quality)")
            else:
                print("ℹ Using OpenStreetMap tiles")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'POI-Blueprint-Quality-Inspector/1.0'
        })
    
    def fetch_poi_image(self, polygon: Polygon, buffer_meters: float = 50) -> Tuple[Image.Image, Tuple[float, float, float, float]]:
        """
        Fetch satellite imagery for a POI polygon.
        
        Args:
            polygon: POI polygon in WGS84 coordinates
            buffer_meters: Buffer around polygon in meters
        
        Returns:
            Tuple of (PIL Image, (min_lon, min_lat, max_lon, max_lat))
        """
        # Get polygon bounds with buffer
        min_lon, min_lat, max_lon, max_lat = get_polygon_bounds(polygon)
        min_lon, min_lat, max_lon, max_lat = expand_bounds(
            min_lon, min_lat, max_lon, max_lat, buffer_meters
        )
        
        # Calculate tile range
        # Top-left corner (min_lon, max_lat)
        x_min, y_min = lat_lon_to_tile(max_lat, min_lon, self.zoom)
        # Bottom-right corner (max_lon, min_lat)
        x_max, y_max = lat_lon_to_tile(min_lat, max_lon, self.zoom)
        
        # Ensure min < max
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min
        
        # Fetch tiles
        tiles = []
        for y in range(y_min, y_max + 1):
            row = []
            for x in range(x_min, x_max + 1):
                tile = self._fetch_tile(x, y, self.zoom)
                row.append(tile)
            tiles.append(row)
        
        # Stitch tiles together
        stitched = self._stitch_tiles(tiles)
        
        # Resize if too large
        if max(stitched.size) > settings.max_image_size:
            ratio = settings.max_image_size / max(stitched.size)
            new_size = (int(stitched.width * ratio), int(stitched.height * ratio))
            stitched = stitched.resize(new_size, Image.Resampling.LANCZOS)
        
        # Return image and the bounds of the area covered
        # Note: The actual bounds might be slightly larger due to tile alignment
        # But for this application, using the requested bounds is a close enough approximation
        return stitched, (min_lon, min_lat, max_lon, max_lat)
    
    def _fetch_tile(self, x: int, y: int, zoom: int) -> Image.Image:
        """
        Fetch a single map tile, with caching.
        
        Args:
            x, y: Tile coordinates
            time.sleep(0.1)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            tile = Image.open(BytesIO(response.content))
            
            # Cache the tile
            tile.save(cache_path)
            
            return tile
        
        except Exception as e:
            print(f"Error fetching tile {x},{y},{zoom}: {e}")
            # Return blank tile on error
            return Image.new('RGB', (256, 256), color='gray')
    
    def _stitch_tiles(self, tiles: list) -> Image.Image:
        """
        Stitch multiple tiles into a single image.
        
        Args:
            tiles: 2D list of PIL Images
        
        Returns:
            Stitched PIL Image
        """
        if not tiles or not tiles[0]:
            raise ValueError("No tiles to stitch")
        
        tile_size = 256  # Standard tile size
        rows = len(tiles)
        cols = len(tiles[0])
        
        # Create blank canvas
        width = cols * tile_size
        height = rows * tile_size
        stitched = Image.new('RGB', (width, height))
        
        # Paste tiles
        for row_idx, row in enumerate(tiles):
            for col_idx, tile in enumerate(row):
                x = col_idx * tile_size
                y = row_idx * tile_size
                stitched.paste(tile, (x, y))
        
        return stitched
    
    def get_cache_key(self, polygon: Polygon) -> str:
        """Generate cache key for a polygon."""
        coords_str = str(sorted(polygon.exterior.coords))
        return hashlib.md5(coords_str.encode()).hexdigest()
