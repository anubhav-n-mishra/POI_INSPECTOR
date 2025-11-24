"""API routes for POI Blueprint Quality Inspector."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import numpy as np
from datetime import datetime

from modules.satellite_fetcher import SatelliteFetcher
from modules.building_detector import BuildingDetector
from modules.polygon_analyzer import PolygonAnalyzer
from modules.quality_scorer import QualityScorer
from modules.report_generator import ReportGenerator
# from modules.ai_suggestions import AISuggestionGenerator  # Disabled - requires google-generativeai
from utils.geo_utils import validate_geojson_polygon
from shapely.geometry import Polygon, mapping
from config import settings


router = APIRouter()

# Initialize modules
satellite_fetcher = SatelliteFetcher()
building_detector = BuildingDetector()
polygon_analyzer = PolygonAnalyzer()
quality_scorer = QualityScorer()
report_generator = ReportGenerator()

# Initialize AI suggestions (optional) - Disabled for now
ai_suggester = None
# if settings.use_ai_suggestions and settings.gemini_api_key:
#     try:
#         ai_suggester = AISuggestionGenerator(settings.gemini_api_key)
#     except Exception as e:
#         print(f"⚠ AI suggestions disabled: {e}")


class POIAnalysisRequest(BaseModel):
    """Request model for POI analysis."""
    poi_id: str = Field(..., description="Unique POI identifier")
    polygon: Dict = Field(..., description="GeoJSON polygon geometry")
    metadata: Optional[Dict] = Field(default={}, description="Additional POI metadata")
    adjacent_pois: Optional[List[Dict]] = Field(default=[], description="Nearby POI polygons for overlap detection")


class POIAnalysisResponse(BaseModel):
    """Response model for POI analysis."""
    poi_id: str
    quality_score: float
    quality_grade: str
    quality_status: Dict
    metrics: Dict
    suggestions: List[str]
    analysis_id: str
    timestamp: str


@router.post("/analyze", response_model=POIAnalysisResponse)
async def analyze_poi(request: POIAnalysisRequest):
    """
    Analyze POI polygon quality.
    
    This endpoint performs complete analysis:
    1. Fetches satellite imagery
    2. Detects building footprint
    3. Calculates quality metrics
    4. Generates suggestions
    5. Computes overall quality score
    """
    try:
        # Validate and parse polygon
        poi_polygon = validate_geojson_polygon(request.polygon.get('coordinates', []))
        
        # Parse adjacent POIs if provided
        adjacent_polygons = []
        if request.adjacent_pois:
            for adj_poi in request.adjacent_pois:
                try:
                    adj_poly = validate_geojson_polygon(adj_poi.get('coordinates', []))
                    adjacent_polygons.append(adj_poly)
                except:
                    continue
        
        # Step 1: Fetch satellite imagery
        satellite_image, bounds = satellite_fetcher.fetch_poi_image(poi_polygon)
        min_lon, min_lat, max_lon, max_lat = bounds
        img_w, img_h = satellite_image.size
        
        # Step 2: Detect buildings
        building_polygons_pixels = building_detector.detect_buildings(satellite_image)
        print(f"  Detected {len(building_polygons_pixels) if building_polygons_pixels else 0} building polygons")
        
        # Convert pixels to Lat/Lon
        building_polygons_geo = []
        if building_polygons_pixels:
            for poly_px in building_polygons_pixels:
                # poly_px is shape (N, 2) where each point is (x, y)
                # Map x (0..w) to lon (min..max)
                # Map y (0..h) to lat (max..min) - NOTE: y is inverted in images (0 is top)
                
                poly_geo = []
                for x, y in poly_px:
                    lon = min_lon + (x / img_w) * (max_lon - min_lon)
                    lat = max_lat - (y / img_h) * (max_lat - min_lat)
                    poly_geo.append([lon, lat])
                
                building_polygons_geo.append(np.array(poly_geo, dtype=np.float32))
        
        # Get primary building (closest to POI)
        # We use the geo polygons now
        primary_building = building_detector.get_primary_building(building_polygons_geo)
        print(f"  Primary building found: {primary_building is not None}")
        
        if primary_building is None:
            # No building detected - create metrics for this case
            metrics = {
                'iou': 0.0,
                'leakage_percentage': 100.0,
                'coverage_percentage': 0.0,
                'regularity_score': polygon_analyzer.calculate_irregularity(poi_polygon),
                'road_overlap_percentage': 0.0,
                'adjacent_overlap': polygon_analyzer.check_adjacent_overlap(poi_polygon, adjacent_polygons)
            }
            suggestions = ["⚠️ No building detected in satellite imagery", 
                          "🔍 POI location may be incorrect or imagery unavailable"]
        else:
            # Step 3: Calculate metrics
            # Convert numpy array to Shapely Polygon
            try:
                building_shapely = Polygon(primary_building)
            except:
                # If conversion fails, treat as no building detected
                metrics = {
                    'iou': 0.0,
                    'leakage_percentage': 100.0,
                    'coverage_percentage': 0.0,
                    'regularity_score': polygon_analyzer.calculate_irregularity(poi_polygon),
                    'road_overlap_percentage': 0.0,
                    'adjacent_overlap': polygon_analyzer.check_adjacent_overlap(poi_polygon, adjacent_polygons)
                }
                suggestions = ["⚠️ Building detected but polygon conversion failed"]
            else:
                metrics = {
                    'iou': polygon_analyzer.calculate_iou(poi_polygon, building_shapely),
                    'leakage_percentage': polygon_analyzer.calculate_leakage(poi_polygon, building_shapely),
                    'coverage_percentage': polygon_analyzer.calculate_coverage(poi_polygon, building_shapely),
                    'regularity_score': polygon_analyzer.calculate_irregularity(poi_polygon),
                    'road_overlap_percentage': polygon_analyzer.calculate_road_overlap(poi_polygon),
                    'adjacent_overlap': polygon_analyzer.check_adjacent_overlap(poi_polygon, adjacent_polygons)
                }
                
                # Step 4: Generate suggestions
                suggestions = polygon_analyzer.suggest_corrections(poi_polygon, building_shapely, metrics)
                
                # Add AI-powered suggestions if available
                if ai_suggester:
                    try:
                        ai_suggestions = ai_suggester.generate_suggestions(metrics, request.metadata)
                        if ai_suggestions:
                            suggestions.append("") # Separator
                            suggestions.append("🤖 AI-Powered Suggestions:")
                            suggestions.extend(ai_suggestions)
                    except Exception as e:
                        print(f"⚠ AI suggestion generation failed: {e}")
        
        # Step 5: Calculate quality score
        quality_score = quality_scorer.calculate_quality_score(metrics)
        quality_grade = quality_scorer.get_quality_grade(quality_score)
        quality_status = quality_scorer.get_quality_status(quality_score)
        
        # Generate analysis ID
        analysis_id = f"{request.poi_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare response
        response = POIAnalysisResponse(
            poi_id=request.poi_id,
            quality_score=quality_score,
            quality_grade=quality_grade,
            quality_status=quality_status,
            metrics=metrics,
            suggestions=suggestions,
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat()
        )
        
        return response
    
    except ValueError as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/upload")
async def upload_geojson(file: UploadFile = File(...)):
    """
    Upload GeoJSON file with POI polygons for batch analysis.
    
    Returns list of POI IDs that can be analyzed.
    """
    try:
        content = await file.read()
        geojson_data = json.loads(content)
        
        # Extract POIs
        pois = []
        if geojson_data.get('type') == 'FeatureCollection':
            for feature in geojson_data.get('features', []):
                if feature.get('geometry', {}).get('type') == 'Polygon':
                    poi_id = feature.get('properties', {}).get('id', f"poi_{len(pois)}")
                    pois.append({
                        'poi_id': poi_id,
                        'geometry': feature['geometry'],
                        'properties': feature.get('properties', {})
                    })
        
        return {
            'status': 'success',
            'poi_count': len(pois),
            'pois': pois
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/report/{analysis_id}")
async def generate_report(analysis_id: str, analysis_data: Dict):
    """
    Generate PDF report for an analysis.
    
    Args:
        analysis_id: Unique analysis identifier
        analysis_data: Complete analysis results
    
    Returns:
        Path to generated PDF report
    """
    try:
        report_path = report_generator.generate_report(
            analysis_data,
            output_filename=f"report_{analysis_id}.pdf"
        )
        
        return {
            'status': 'success',
            'report_path': str(report_path),
            'analysis_id': analysis_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'service': 'POI Blueprint Quality Inspector',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }
