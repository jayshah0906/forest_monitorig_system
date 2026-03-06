# Forest Monitoring System - Dang District

AI-Driven Forest Monitoring & Analytics for Dang District, Gujarat

## Project Structure

This repository contains the complete Forest Monitoring System built for a 48-hour hackathon.

```
forest_monitoring/
├── frontend/          # Next.js React frontend
├── backend/           # FastAPI backend (to be added by backend dev)
└── ml_models/         # ML models (to be added by ML engineer)
```

## Team

- **Frontend Developer**: React/Next.js dashboard
- **Backend Developer**: FastAPI + Geospatial processing
- **ML Engineer**: DeepForest + Species Classification

## Quick Start

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Backend (when ready)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API runs at http://localhost:8000
```

## Features

- 🌲 Automated tree counting (>85% accuracy)
- 🌿 Species identification (5 species)
- 📊 NDVI-based forest health assessment
- 🗺️ Interactive map with area selection
- 📈 Real-time analytics dashboard
- 📥 Downloadable reports

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Leaflet, Recharts, TailwindCSS
- **Backend**: FastAPI, Rasterio, GeoPandas, NumPy, Pandas
- **ML**: DeepForest, TensorFlow/PyTorch, EfficientNet

## Timeline

- **Hour 12**: Individual components working
- **Hour 24**: Mock integration
- **Hour 36**: Real integration working
- **Hour 42**: Final testing and demo prep
- **Hour 48**: Demo + PPT presentation

## License

MIT License - Hackathon Project 2026
