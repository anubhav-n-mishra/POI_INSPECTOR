# How to Test the POI Quality Inspector

## Option 1: Use the Provided Sample File

**Location:** `e:\POI\examples\sample_poi.geojson`

This file contains 3 POIs:
- Target Store in San Francisco
- Walmart in Los Angeles  
- Starbucks in Seattle

**To use it:**
1. Open http://localhost:3000
2. Click "Upload GeoJSON"
3. Navigate to `e:\POI\examples\sample_poi.geojson`
4. Select the file
5. View the analysis results!

---

## Option 2: Create Your Own GeoJSON

You can create a GeoJSON file for any location using these tools:

### Online Tools:
1. **geojson.io** (https://geojson.io)
   - Draw polygons on a map
   - Export as GeoJSON
   - Best for custom locations

2. **Google My Maps**
   - Create shapes
   - Export as KML, then convert to GeoJSON

3. **QGIS** (Desktop GIS software)
   - Professional tool for creating POI polygons

### GeoJSON Format:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "your_poi_id",
        "name": "Store Name",
        "address": "123 Main St"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [longitude, latitude],
            [longitude, latitude],
            [longitude, latitude],
            [longitude, latitude],
            [longitude, latitude]
          ]
        ]
      }
    }
  ]
}
```

**Important:** 
- Coordinates are `[longitude, latitude]` (not lat, lon!)
- First and last coordinate must be the same (closed polygon)
- Use at least 4 points to make a polygon

---

## Option 3: Use Demo Mode

If you just want to see how it works:
1. Open http://localhost:3000
2. Click "Run Demo Analysis"
3. Instantly see results with mock data

---

## Testing Tips

1. **Start with the sample file** to verify everything works
2. **Try different POI sizes** - small buildings vs large stores
3. **Test edge cases** - irregular shapes, overlapping polygons
4. **Check the backend logs** to see the analysis process

---

## Troubleshooting

**File upload not working?**
- Make sure backend is running at http://localhost:8000
- Check the file is valid GeoJSON format
- Try the demo mode first

**No analysis results?**
- Check browser console (F12) for errors
- Verify the GeoJSON has valid coordinates
- Ensure the polygon is closed (first = last point)
