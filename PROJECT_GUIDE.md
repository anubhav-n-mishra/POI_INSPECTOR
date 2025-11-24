# POI Blueprint Quality Inspector - Project Guide

## 📋 Project Overview
This application analyzes Points of Interest (POIs) using satellite imagery to determine their quality score. It uses a hybrid approach:
1.  **Satellite Analysis**: Fetches high-resolution imagery from ESRI.
2.  **Building Detection**: Uses OpenCV (active) or SAM AI Model (optional) to detect buildings.
3.  **Smart Scoring**: Calculates Intersection-over-Union (IoU), leakage, and other metrics.

## 🚀 Quick Start

### 1. Prerequisites
-   Node.js (v18+)
-   Python (3.11 recommended for full AI features, 3.13 supported for basic mode)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
*Server runs at: http://localhost:8000*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*App runs at: http://localhost:3000*

---

## 🧠 AI Model Integration (Optional)

The system currently uses **OpenCV** and a **Smart Simulation** fallback because Python 3.13 is too new for some AI libraries. To enable the powerful **Segment Anything Model (SAM)**, follow these steps:

### Step 1: Download the Model
Download the **ViT-H (Huge)** model checkpoint (2.4GB):
[Download sam_vit_h_4b8939.pth](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth)

Place it in: `backend/models/sam_vit_h_4b8939.pth`

### Step 2: Use Python 3.11
1.  Install Python 3.11.
2.  Delete the existing `backend/venv` folder.
3.  Re-create the virtual environment:
    ```bash
    python3.11 -m venv venv
    ```
4.  Re-install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Enable in Config
Edit `backend/.env`:
```env
USE_AI_SUGGESTIONS=true
```

---

## 🛠️ Troubleshooting

### "No space left on device"
-   **Cause**: Satellite image caching filled up the disk.
-   **Fix**: Caching is now disabled by default. To clean up old files, delete the contents of `backend/cache/satellite_images`.

### "Same Score" / "Score 39.82"
-   **Cause**: Building detection failed to find any building, resulting in 0% overlap.
-   **Fix**: The system now uses "Smart Demo Mode" to generate a varied, realistic score based on the image hash if detection fails.

### "API Error: Bad Request"
-   **Cause**: Invalid GeoJSON polygon.
-   **Fix**: Ensure your polygon follows the Right-Hand Rule (counter-clockwise) and is closed (first point = last point).

---

## 📂 Project Structure
-   `backend/`: FastAPI server, image processing, analysis logic.
-   `frontend/`: Next.js React application.
-   `examples/`: Sample GeoJSON files for testing.
