"""Quality scoring system for POI polygons."""
from typing import Dict
from config import settings


class QualityScorer:
    """Calculates overall quality score for POI polygons."""
    
    def __init__(self):
        self.weights = {
            'iou': settings.weight_iou,
            'leakage': settings.weight_leakage,
            'road_overlap': settings.weight_road_overlap,
            'regularity': settings.weight_regularity,
            'adjacent_overlap': settings.weight_adjacent_overlap
        }
    
    def calculate_quality_score(self, metrics: Dict) -> float:
        """
        Calculate overall quality score (0-100) from individual metrics.
        
        Scoring formula:
        Quality = w1*IOU + w2*(100-leakage) + w3*(100-road_overlap) + 
                  w4*regularity + w5*(100-adjacent_overlap)
        
        Args:
            metrics: Dictionary of analysis metrics
        
        Returns:
            Quality score (0-100)
        """
        # Extract metrics with defaults
        iou = metrics.get('iou', 0) * 100  # Convert to percentage
        leakage = metrics.get('leakage_percentage', 100)
        road_overlap = metrics.get('road_overlap_percentage', 0)
        regularity = metrics.get('regularity_score', 50)
        adjacent_overlap = metrics.get('adjacent_overlap', {}).get('total_overlap_percentage', 0)
        
        # Calculate weighted score
        score = (
            self.weights['iou'] * iou +
            self.weights['leakage'] * (100 - leakage) +
            self.weights['road_overlap'] * (100 - road_overlap) +
            self.weights['regularity'] * regularity +
            self.weights['adjacent_overlap'] * (100 - adjacent_overlap)
        )
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        return round(score, 2)
    
    def get_quality_grade(self, score: float) -> str:
        """
        Get letter grade for quality score.
        
        Args:
            score: Quality score (0-100)
        
        Returns:
            Letter grade (A+ to F)
        """
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def get_quality_status(self, score: float) -> Dict[str, str]:
        """
        Get quality status with color coding.
        
        Args:
            score: Quality score (0-100)
        
        Returns:
            Dict with status, color, and emoji
        """
        if score >= 85:
            return {
                'status': 'Excellent',
                'color': '#10b981',  # green
                'emoji': '🟢',
                'description': 'POI polygon is highly accurate'
            }
        elif score >= 70:
            return {
                'status': 'Good',
                'color': '#3b82f6',  # blue
                'emoji': '🔵',
                'description': 'POI polygon is acceptable with minor issues'
            }
        elif score >= 50:
            return {
                'status': 'Fair',
                'color': '#f59e0b',  # orange
                'emoji': '🟡',
                'description': 'POI polygon needs improvement'
            }
        else:
            return {
                'status': 'Poor',
                'color': '#ef4444',  # red
                'emoji': '🔴',
                'description': 'POI polygon requires significant correction'
            }
    
    def get_metric_status(self, metric_name: str, value: float) -> Dict[str, str]:
        """
        Get status for individual metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        
        Returns:
            Dict with status and color
        """
        if metric_name == 'iou':
            # IOU: higher is better
            if value >= 0.7:
                return {'status': 'Good', 'color': '#10b981'}
            elif value >= 0.5:
                return {'status': 'Fair', 'color': '#f59e0b'}
            else:
                return {'status': 'Poor', 'color': '#ef4444'}
        
        elif metric_name in ['leakage_percentage', 'road_overlap_percentage', 'adjacent_overlap']:
            # Percentages: lower is better
            if value <= 10:
                return {'status': 'Good', 'color': '#10b981'}
            elif value <= 25:
                return {'status': 'Fair', 'color': '#f59e0b'}
            else:
                return {'status': 'Poor', 'color': '#ef4444'}
        
        elif metric_name == 'regularity_score':
            # Regularity: higher is better
            if value >= 60:
                return {'status': 'Good', 'color': '#10b981'}
            elif value >= 40:
                return {'status': 'Fair', 'color': '#f59e0b'}
            else:
                return {'status': 'Poor', 'color': '#ef4444'}
        
        elif metric_name == 'coverage_percentage':
            # Coverage: higher is better
            if value >= 80:
                return {'status': 'Good', 'color': '#10b981'}
            elif value >= 60:
                return {'status': 'Fair', 'color': '#f59e0b'}
            else:
                return {'status': 'Poor', 'color': '#ef4444'}
        
        return {'status': 'Unknown', 'color': '#6b7280'}
