# POI Blueprint Quality Inspector - Backend

Python backend for POI polygon quality analysis.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
copy .env.example .env
# Edit .env with your settings
```

4. Run server:
```bash
python main.py
# or
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

## API Documentation

Interactive API docs: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── api/
│   └── routes.py       # API endpoints
├── modules/
│   ├── satellite_fetcher.py    # Satellite imagery fetching
│   ├── building_detector.py    # Building detection
│   ├── polygon_analyzer.py     # Polygon analysis
│   ├── quality_scorer.py       # Quality scoring
│   └── report_generator.py     # PDF report generation
└── utils/
    └── geo_utils.py    # Geographic utilities
```
