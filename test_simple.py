import requests
import json

# Load sample GeoJSON
with open('examples/sample_poi.geojson', 'r') as f:
    geojson = json.load(f)

feature = geojson['features'][0]

payload = {
    "poi_id": feature['properties']['id'],
    "polygon": feature['geometry'],
    "metadata": feature['properties']
}

print("Testing POI Analysis API")
print("POI:", payload['metadata']['name'])

try:
    response = requests.post(
        'http://localhost:8000/api/analyze',
        json=payload,
        timeout=60
    )
    
    print("Status:", response.status_code)
    
    if response.status_code == 200:
        result = response.json()
        print("\nSUCCESS!")
        print("Quality Score:", result['quality_score'])
        print("Grade:", result['quality_grade'])
        print("\nMetrics:")
        for key, value in result['metrics'].items():
            print(f"  {key}: {value}")
    else:
        print("ERROR:", response.text[:200])
        
except Exception as e:
    print("FAILED:", str(e))
