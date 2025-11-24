"""AI-powered suggestion generator using Google Gemini."""
import os
from typing import List, Dict, Optional
import google.generativeai as genai


class AISuggestionGenerator:
    """Generate intelligent improvement suggestions using Gemini AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini AI suggestion generator.
        
        Args:
            api_key: Google Gemini API key (optional, reads from env)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✓ Gemini AI suggestions enabled")
            except Exception as e:
                print(f"⚠ Gemini AI initialization failed: {e}")
                self.enabled = False
        else:
            print("ℹ Gemini API key not found - using rule-based suggestions")
    
    def generate_suggestions(self, metrics: Dict, poi_data: Dict) -> List[str]:
        """
        Generate AI-powered improvement suggestions.
        
        Args:
            metrics: Quality metrics dictionary
            poi_data: POI metadata (name, category, etc.)
        
        Returns:
            List of actionable suggestion strings
        """
        if not self.enabled:
            return []
        
        try:
            prompt = self._build_prompt(metrics, poi_data)
            response = self.model.generate_content(prompt)
            suggestions = self._parse_response(response.text)
            return suggestions
        except Exception as e:
            print(f"⚠ Gemini API error: {e}")
            return []
    
    def _build_prompt(self, metrics: Dict, poi_data: Dict) -> str:
        """Build the Gemini prompt for suggestion generation."""
        
        poi_name = poi_data.get('name', 'Unknown POI')
        poi_category = poi_data.get('category', 'Unknown')
        
        prompt = f"""You are a geospatial data quality expert analyzing POI polygon accuracy.

POI Information:
- Name: {poi_name}
- Category: {poi_category}

Quality Metrics:
- IOU Score: {metrics.get('iou', 0):.3f} (0-1 scale, 1.0 = perfect alignment)
- Leakage: {metrics.get('leakage_percentage', 0):.1f}% (polygon area outside building)
- Coverage: {metrics.get('coverage_percentage', 0):.1f}% (building area covered by polygon)
- Regularity: {metrics.get('regularity_score', 0):.1f}/100 (shape regularity)
- Road Overlap: {metrics.get('road_overlap_percentage', 0):.1f}%

Analysis Context:
- IOU < 0.5 = Poor alignment
- IOU 0.5-0.7 = Moderate alignment
- IOU > 0.7 = Good alignment
- Leakage > 25% = Significant excess area
- Coverage < 70% = Insufficient building coverage
- Regularity < 40 = Irregular shape

Task: Provide 3-5 specific, actionable suggestions to improve this POI polygon quality.

Requirements:
1. Be specific and technical
2. Mention directional adjustments (north, south, east, west) when relevant
3. Suggest measurements or percentages when possible
4. Prioritize the most impactful improvements
5. Keep each suggestion concise (1-2 sentences)

Format: Return ONLY a numbered list, one suggestion per line. No introduction or conclusion."""

        return prompt
    
    def _parse_response(self, response_text: str) -> List[str]:
        """Parse Gemini response into list of suggestions."""
        
        # Split by newlines and filter
        lines = response_text.strip().split('\n')
        suggestions = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and headers
            if not line or line.lower().startswith(('here', 'suggestion', 'based on')):
                continue
            
            # Remove numbering if present
            if line[0].isdigit() and ('. ' in line or ') ' in line):
                line = line.split('. ', 1)[-1].split(') ', 1)[-1]
            
            # Remove markdown formatting
            line = line.replace('**', '').replace('*', '')
            
            if line:
                suggestions.append(line.strip())
        
        return suggestions[:5]  # Limit to 5 suggestions
