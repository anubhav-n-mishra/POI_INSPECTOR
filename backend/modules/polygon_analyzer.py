"""Polygon analysis and quality metrics calculation."""
import math
from typing import Dict, List, Tuple, Optional
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import nearest_points
import numpy as np

from utils.geo_utils import polygon_to_meters, calculate_distance


class PolygonAnalyzer:
    """Analyzes POI polygon quality against detected building footprint."""
    
    def calculate_iou(self, polygon1: Polygon, polygon2: Polygon) -> float:
        """
        Calculate Intersection over Union (IOU) between two polygons.
        
        Args:
            polygon1: First polygon
            polygon2: Second polygon
        
        Returns:
            IOU score (0-1)
        """
        try:
            intersection = polygon1.intersection(polygon2).area
            union = polygon1.union(polygon2).area
            
            if union == 0:
                return 0.0
            
            return intersection / union
        except:
            return 0.0
    
    def calculate_leakage(self, poi_polygon: Polygon, building_polygon: Polygon) -> float:
        """
        Calculate percentage of POI area outside building footprint.
        
        Args:
            poi_polygon: POI polygon
            building_polygon: Detected building polygon
        
        Returns:
            Leakage percentage (0-100)
        """
        try:
            poi_area = poi_polygon.area
            if poi_area == 0:
                return 100.0
            
            outside_area = poi_polygon.difference(building_polygon).area
            return (outside_area / poi_area) * 100
        except:
            return 100.0
    
    def calculate_coverage(self, poi_polygon: Polygon, building_polygon: Polygon) -> float:
        """
        Calculate percentage of building covered by POI.
        
        Args:
            poi_polygon: POI polygon
            building_polygon: Detected building polygon
        
        Returns:
            Coverage percentage (0-100)
        """
        try:
            building_area = building_polygon.area
            if building_area == 0:
                return 0.0
            
            covered_area = poi_polygon.intersection(building_polygon).area
            return (covered_area / building_area) * 100
        except:
            return 0.0
    
    def calculate_irregularity(self, polygon: Polygon) -> float:
        """
        Calculate polygon irregularity score based on shape complexity.
        
        A regular polygon (rectangle, square) scores high.
        An irregular polygon scores low.
        
        Args:
            polygon: Polygon to analyze
        
        Returns:
            Regularity score (0-100)
        """
        try:
            # Use isoperimetric quotient: 4π * area / perimeter²
            # Circle = 1.0, Square ≈ 0.785, irregular shapes < 0.5
            area = polygon.area
            perimeter = polygon.length
            
            if perimeter == 0:
                return 0.0
            
            ipq = (4 * math.pi * area) / (perimeter ** 2)
            
            # Normalize to 0-100 scale
            # Buildings are typically rectangular, so we expect 0.6-0.8
            score = min(100, ipq * 125)  # Scale so 0.8 = 100
            
            return score
        except:
            return 50.0
    
    def calculate_road_overlap(self, polygon: Polygon, 
                               road_polygons: List[Polygon] = None) -> float:
        """
        Calculate percentage of POI overlapping with roads/parking.
        
        Note: This is a simplified version. In production, fetch actual road data from OSM.
        
        Args:
            polygon: POI polygon
            road_polygons: List of road polygons (optional)
        
        Returns:
            Road overlap percentage (0-100)
        """
        # Simplified: assume no road data available
        # In production, query OpenStreetMap Overpass API for roads
        if not road_polygons:
            return 0.0
        
        try:
            total_overlap = 0
            for road in road_polygons:
                overlap = polygon.intersection(road).area
                total_overlap += overlap
            
            poi_area = polygon.area
            if poi_area == 0:
                return 0.0
            
            return (total_overlap / poi_area) * 100
        except:
            return 0.0
    
    def check_adjacent_overlap(self, polygon: Polygon, 
                              adjacent_polygons: List[Polygon]) -> Dict:
        """
        Check for overlaps with adjacent POIs.
        
        Args:
            polygon: POI polygon to check
            adjacent_polygons: List of nearby POI polygons
        
        Returns:
            Dict with overlap info
        """
        overlaps = []
        total_overlap_area = 0
        
        for idx, adj_poly in enumerate(adjacent_polygons):
            try:
                if polygon.intersects(adj_poly):
                    overlap_area = polygon.intersection(adj_poly).area
                    overlap_pct = (overlap_area / polygon.area) * 100
                    
                    overlaps.append({
                        'index': idx,
                        'overlap_area': overlap_area,
                        'overlap_percentage': overlap_pct
                    })
                    total_overlap_area += overlap_area
            except:
                continue
        
        total_overlap_pct = (total_overlap_area / polygon.area * 100) if polygon.area > 0 else 0
        
        return {
            'has_overlap': len(overlaps) > 0,
            'overlap_count': len(overlaps),
            'overlaps': overlaps,
            'total_overlap_percentage': total_overlap_pct
        }
    
    def suggest_corrections(self, poi_polygon: Polygon, building_polygon: Polygon,
                           metrics: Dict) -> List[str]:
        """
        Generate correction suggestions based on analysis.
        
        Args:
            poi_polygon: Original POI polygon
            building_polygon: Detected building polygon
            metrics: Analysis metrics
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # IOU-based suggestions
        iou = metrics.get('iou', 0)
        if iou < 0.5:
            suggestions.append("⚠️ Poor alignment: POI polygon does not match building footprint")
        elif iou < 0.7:
            suggestions.append("⚡ Moderate alignment: Consider adjusting polygon boundaries")
        
        # Leakage suggestions
        leakage = metrics.get('leakage_percentage', 0)
        if leakage > 30:
            suggestions.append(f"🔴 High leakage ({leakage:.1f}%): Shrink polygon to match building")
            # Determine which sides to shrink
            directions = self._analyze_leakage_directions(poi_polygon, building_polygon)
            for direction in directions:
                suggestions.append(f"  → Shrink {direction}")
        elif leakage > 15:
            suggestions.append(f"🟡 Moderate leakage ({leakage:.1f}%): Minor boundary adjustments needed")
        
        # Coverage suggestions
        coverage = metrics.get('coverage_percentage', 0)
        if coverage < 70:
            suggestions.append(f"📏 Low coverage ({coverage:.1f}%): POI may be too small or misaligned")
        
        # Irregularity suggestions
        regularity = metrics.get('regularity_score', 100)
        if regularity < 40:
            suggestions.append("🔷 Irregular shape: Consider simplifying polygon to rectangular form")
        
        # Adjacent overlap suggestions
        if metrics.get('adjacent_overlap', {}).get('has_overlap'):
            overlap_pct = metrics['adjacent_overlap']['total_overlap_percentage']
            suggestions.append(f"⚡ Overlaps with {metrics['adjacent_overlap']['overlap_count']} adjacent POI(s) ({overlap_pct:.1f}%)")
            if overlap_pct > 20:
                suggestions.append("  → Consider splitting or merging POIs")
        
        if not suggestions:
            suggestions.append("✅ POI polygon quality is good!")
        
        return suggestions
    
    def _analyze_leakage_directions(self, poi_polygon: Polygon, 
                                   building_polygon: Polygon) -> List[str]:
        """Determine which directions have leakage."""
        directions = []
        
        try:
            # Get centroids
            poi_center = poi_polygon.centroid
            building_center = building_polygon.centroid
            
            # Get bounds
            poi_bounds = poi_polygon.bounds
            building_bounds = building_polygon.bounds
            
            # Check each direction
            if poi_bounds[0] < building_bounds[0] - 5:  # West
                directions.append("west side")
            if poi_bounds[2] > building_bounds[2] + 5:  # East
                directions.append("east side")
            if poi_bounds[1] < building_bounds[1] - 5:  # South
                directions.append("south side")
            if poi_bounds[3] > building_bounds[3] + 5:  # North
                directions.append("north side")
        except:
            pass
        
        return directions if directions else ["all sides"]
