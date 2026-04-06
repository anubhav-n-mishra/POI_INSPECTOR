# POI Blueprint Quality Inspector (PBQI)

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> **A real-time AI system that verifies and improves Point-of-Interest polygon accuracy using satellite imagery and pretrained models.**

## 🎯 Overview

POI Blueprint Quality Inspector is an AI-powered tool designed for advertising platforms like GroundTruth that rely on high-precision POI boundaries. The system automatically:

- ✅ Fetches satellite imagery for any POI location
- ✅ Detects building footprints using computer vision
- ✅ Calculates quality metrics (IOU, leakage, coverage, etc.)
- ✅ Generates a 0-100 quality score
- ✅ Provides actionable correction suggestions
- ✅ Creates detailed PDF reports

## 🚀 Features

### 1️⃣ Building Footprint Detection
Uses pretrained computer vision models to detect actual building boundaries from satellite imagery.

### 2️⃣ Comprehensive Quality Metrics
- **IOU (Intersection over Union)**: Polygon alignment accuracy
- **Leakage**: Percentage of POI area outside building
- **Coverage**: Percentage of building covered by POI
- **Regularity**: Shape complexity analysis
- **Road Overlap**: Detection of polygon covering roads/parking
- **Adjacent POI Overlap**: Conflicts with nearby POIs

### 3️⃣ Blueprint Quality Score (0-100)
Weighted scoring system combining all metrics to provide a single quality indicator.

### 4️⃣ Smart Suggestions
AI-generated recommendations like:
- "Shrink polygon on east side by 5m"
- "Boundary does not match building footprint"
- "Split into two separate POIs"

### 5️⃣ Interactive Dashboard
Beautiful, modern UI with:
- Real-time analysis
- Visual metrics display
- Quality gauge
- Suggestions panel
- PDF report download

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Run server
python main.py
```

Backend will run at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run at `http://localhost:3000`

## 🎮 Usage

### Option 1: Upload GeoJSON

1. Open `http://localhost:3000`
2. Click "Upload GeoJSON"
3. Select a `.geojson` file with POI polygons
4. View analysis results

### Option 2: Try Demo

1. Click "Try Demo Analysis" on the homepage
2. See sample analysis with mock data

### Option 3: API Direct

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "poi_id": "store_001",
    "polygon": {
      "type": "Polygon",
      "coordinates": [[[-122.4194, 37.7749], ...]]
    },
    "metadata": {
      "name": "Target Store",
      "address": "123 Main St"
    }
  }'
```

## 📊 API Documentation

Interactive API docs available at: `http://localhost:8000/docs`

### Main Endpoints

#### POST `/api/analyze`
Analyze POI polygon quality

**Request:**
```json
{
  "poi_id": "string",
  "polygon": {
    "type": "Polygon",
    "coordinates": [[[lon, lat], ...]]
  },
  "metadata": {},
  "adjacent_pois": []
}
```

**Response:**
```json
{
  "poi_id": "string",
  "quality_score": 78.5,
  "quality_grade": "B",
  "quality_status": {...},
  "metrics": {...},
  "suggestions": [...],
  "analysis_id": "string",
  "timestamp": "ISO8601"
}
```

#### POST `/api/upload`
Upload GeoJSON file for batch analysis

#### POST `/api/report/{analysis_id}`
Generate PDF report

#### GET `/api/health`
Health check

## 🏗️ Architecture

```
POI/
├── backend/                 # FastAPI Python backend
│   ├── main.py             # App entry point
│   ├── config.py           # Configuration
│   ├── api/
│   │   └── routes.py       # API endpoints
│   ├── modules/
│   │   ├── satellite_fetcher.py    # Imagery fetching
│   │   ├── building_detector.py    # CV detection
│   │   ├── polygon_analyzer.py     # Metrics calculation
│   │   ├── quality_scorer.py       # Scoring system
│   │   └── report_generator.py     # PDF generation
│   └── utils/
│       └── geo_utils.py    # Geographic utilities
│
├── frontend/               # Next.js React frontend
│   ├── app/
│   │   ├── page.tsx       # Landing page
│   │   └── globals.css    # Styles
│   └── components/
│       ├── AnalysisView.tsx       # Analysis dashboard
│       ├── MetricsCard.tsx        # Metric display
│       ├── QualityGauge.tsx       # Score gauge
│       └── SuggestionsPanel.tsx   # Suggestions
│
└── examples/
    └── sample_poi.geojson  # Sample data
```

## 🧠 How It Works

1. **Satellite Image Fetching**: Downloads map tiles from OpenStreetMap for the POI area
2. **Building Detection**: Uses OpenCV edge detection and morphological operations to identify buildings
3. **Polygon Analysis**: Calculates IOU, leakage, coverage, and other metrics
4. **Quality Scoring**: Combines metrics with weighted formula to generate 0-100 score
5. **Suggestion Generation**: Rule-based system generates actionable corrections
6. **Report Creation**: Generates PDF with all analysis results

## 🎨 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Shapely & GeoPandas**: Geospatial operations
- **OpenCV & scikit-image**: Computer vision
- **ReportLab**: PDF generation
- **Pillow**: Image processing

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Lucide React**: Icons
- **Canvas API**: Quality gauge visualization

## 📈 Quality Score Formula

```
Quality Score = 
  0.35 × IOU +
  0.25 × (100 - leakage%) +
  0.20 × (100 - road_overlap%) +
  0.10 × regularity_score +
  0.10 × (100 - adjacent_overlap%)
```

Weights can be adjusted in `.env` configuration.

## 🔧 Configuration

Edit `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Scoring Weights (must sum to 1.0)
WEIGHT_IOU=0.35
WEIGHT_LEAKAGE=0.25
WEIGHT_ROAD_OVERLAP=0.20
WEIGHT_REGULARITY=0.10
WEIGHT_ADJACENT_OVERLAP=0.10

# Processing
MAX_IMAGE_SIZE=1024
TILE_ZOOM_LEVEL=18
```

## 🚧 Future Enhancements

- [ ] Integration with Detectron2 or SAM for better building detection
- [ ] Real-time map visualization with Mapbox
- [ ] Batch processing for multiple POIs
- [ ] Historical quality tracking
- [ ] API authentication
- [ ] Cloud deployment (AWS/GCP)
- [ ] Mobile app

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

This is a hackathon/demo project. Contributions welcome!

## 📧 Contact

Created and maintained by **Anubhav Mishra**.

- GitHub: https://github.com/anubhav-n-mishra
- Portfolio: https://linkedin.com/in/anubhav-mishra0
- Website: https://mishraanubhav.me

Built for GroundTruth internship application.

---

**Made by Anubhav Mishra · Portfolio: https://linkedin.com/in/anubhav-mishra0 · Website: https://mishraanubhav.me**
