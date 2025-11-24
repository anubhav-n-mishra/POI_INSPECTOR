# Test Sample GeoJSON Files

## Available Test Files

All test files are located in `e:\POI\examples\` directory.

### 1. **sample_poi.geojson** (Original)
**Location**: San Francisco, Los Angeles, Seattle
- Target Store #1234 (San Francisco, CA)
- Walmart Supercenter (Los Angeles, CA)
- Starbucks Coffee (Seattle, WA)

**Use Case**: Basic retail POI testing

---

### 2. **nyc_landmarks.geojson** (NEW)
**Location**: New York City
- Apple Store Fifth Avenue (iconic glass cube)
- Grand Central Terminal (historic train station)
- Brooklyn Bridge (landmark)

**Use Case**: Famous landmarks, varied building types

---

### 3. **silicon_valley.geojson** (NEW)
**Location**: Silicon Valley, California
- Googleplex (Mountain View, CA)
- Apple Park (Cupertino, CA - circular building)
- Tesla Factory (Fremont, CA - large industrial)

**Use Case**: Tech campuses, large buildings

---

### 4. **seattle_landmarks.geojson** (NEW)
**Location**: Seattle, Washington
- Space Needle (observation tower)
- Pike Place Market (historic market)
- Amazon Spheres (glass domes)

**Use Case**: Unique architecture, mixed use

---

### 5. **chicago_landmarks.geojson** (NEW)
**Location**: Chicago, Illinois
- Willis Tower (Sears Tower - skyscraper)
- Navy Pier (lakefront entertainment)
- Millennium Park (urban park)

**Use Case**: Urban landmarks, parks

---

### 6. **florida_attractions.geojson** (NEW)
**Location**: Florida
- Cinderella Castle (Disney World)
- Universal Studios Orlando
- Kennedy Space Center

**Use Case**: Theme parks, large complexes

---

## How to Test

### Option 1: Frontend Upload
1. Open http://localhost:3000
2. Click "Choose GeoJSON File"
3. Navigate to `e:\POI\examples\`
4. Select any `.geojson` file
5. View analysis results

### Option 2: API Test
```python
import requests
import json

# Load any test file
with open('examples/nyc_landmarks.geojson', 'r') as f:
    geojson = json.load(f)

# Get first POI
feature = geojson['features'][0]

# Analyze
response = requests.post(
    'http://localhost:8000/api/analyze',
    json={
        "poi_id": feature['properties']['id'],
        "polygon": feature['geometry'],
        "metadata": feature['properties']
    }
)

print(response.json())
```

### Option 3: Demo Mode
- Just click "Run Demo Analysis" for instant results

---

## Expected Results

### Quality Scores Will Vary:
- **High (85-100)**: Well-aligned polygons matching building footprints
- **Good (70-84)**: Acceptable alignment with minor issues
- **Fair (50-69)**: Moderate alignment, needs improvement
- **Poor (0-49)**: Significant misalignment or no building detected

### Why Scores May Be Low:
1. **Test Data**: Simplified rectangular polygons
2. **Satellite Imagery**: May not have clear building outlines
3. **Detection**: OpenCV may not detect all buildings
4. **Expected Behavior**: System correctly identifies poor quality

---

## Testing Tips

1. **Start with NYC Landmarks**: Famous buildings, good satellite coverage
2. **Try Silicon Valley**: Large tech campuses should be visible
3. **Test Different Categories**: Retail, office, landmarks, parks
4. **Compare Results**: See how different POI types score
5. **Check Suggestions**: Review improvement recommendations

---

## File Format

All files follow standard GeoJSON format:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "unique_id",
        "name": "POI Name",
        "address": "Full Address",
        "category": "retail|office|landmark|etc",
        "description": "Optional description"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon, lat], [lon, lat], ...]]
      }
    }
  ]
}
```

---

## Creating Your Own

Use https://geojson.io to create custom test data:
1. Draw polygons on the map
2. Add properties (id, name, etc.)
3. Export as GeoJSON
4. Save to `examples/` folder
5. Test in the application

---

## Summary

**6 Test Files Created:**
- ✅ sample_poi.geojson (3 POIs)
- ✅ nyc_landmarks.geojson (3 POIs)
- ✅ silicon_valley.geojson (3 POIs)
- ✅ seattle_landmarks.geojson (3 POIs)
- ✅ chicago_landmarks.geojson (3 POIs)
- ✅ florida_attractions.geojson (3 POIs)

**Total: 18 POIs** across different categories and locations!
