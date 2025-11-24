import requests
import json

# Load sample GeoJSON
with open('examples/sample_poi.geojson', 'r') as f:
    geojson = json.load(f)

# Get first POI
feature = geojson['features'][0]

# Prepare request
payload = {
    "poi_id": feature['properties']['id'],
    "polygon": feature['geometry'],
    "metadata": feature['properties']
}

print("Testing POI Analysis API...")
print(f"POI ID: {payload['poi_id']}")
print(f"POI Name: {payload['metadata']['name']}")

# Make API request
try:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        json=payload,
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✓ Analysis successful!")
        print(f"Quality Score: {result['quality_score']}/100")
        print(f"Grade: {result['quality_grade']}")
        print(f"Status: {result['quality_status']['status']}")
        print(f"\nMetrics:")
        print(f"  - IOU: {result['metrics']['iou']:.2f}")
        print(f"  - Leakage: {result['metrics']['leakage_percentage']:.1f}%")
        print(f"  - Coverage: {result['metrics']['coverage_percentage']:.1f}%")
        print(f"\nSuggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    else:
        print(f"\n✗ Error: {response.text}")
        
except Exception as e:
    print(f"\n✗ Request failed: {str(e)}")
