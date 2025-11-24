"""Configuration management for POI Blueprint Quality Inspector."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Base directory
    base_dir: Path = Path(__file__).parent
    
    # Directories
    model_cache_dir: Path = Path("./models")
    image_cache_dir: str = Field(default="cache/satellite_images", env="IMAGE_CACHE_DIR")
    reports_dir: Path = Path("./reports")
    
    # Satellite imagery settings
    tile_url: str = Field(
        default="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        env="TILE_URL"
    )
    zoom_level: int = Field(default=18, env="ZOOM_LEVEL")
    tile_zoom_level: int = Field(default=18, env="ZOOM_LEVEL")  # Alias for compatibility
    osm_tile_url: str = Field(default="https://tile.openstreetmap.org/{z}/{x}/{y}.png", env="TILE_URL")  # Alias
    
    # API Keys (optional)
    mapbox_token: str = Field(default="", env="MAPBOX_TOKEN")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    google_maps_api_key: Optional[str] = None
    
    # Feature flags
    use_ai_suggestions: bool = Field(default=False, env="USE_AI_SUGGESTIONS")
    use_mapbox: bool = Field(default=False, env="USE_MAPBOX")
    
    # Processing settings
    max_image_size: int = 1024
    cache_expiry_days: int = 7
    
    # Scoring Weights (must sum to 1.0)
    weight_iou: float = 0.35
    weight_leakage: float = 0.25
    weight_road_overlap: float = 0.20
    weight_regularity: float = 0.10
    weight_adjacent_overlap: float = 0.10


# Global settings instance
settings = Settings()

# Create directories if they don't exist
settings.model_cache_dir.mkdir(parents=True, exist_ok=True)
settings.reports_dir.mkdir(parents=True, exist_ok=True)
