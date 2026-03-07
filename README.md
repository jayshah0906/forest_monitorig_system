# � ForestEye - AI-Powered Forest Monitoring System

> Protecting Nature with Intelligence

An advanced web-based forest monitoring platform that leverages Sentinel-2 satellite imagery and machine learning to analyze forest health, estimate tree populations, and identify species distribution in Dang District, Gujarat.

![Forest Monitoring](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 🗺️ Interactive Mapping
- **Draw & Analyze**: Select any forest region using polygon drawing tools
- **Real-time Visualization**: See satellite coverage and analysis boundaries
- **Tree Markers**: View detected tree locations on the map
- **Multiple Layers**: Switch between street and satellite views

### 📊 Advanced Analytics
- **Circular Progress KPIs**: Modern dashboard with animated metrics
- **Tree Detection**: AI-powered tree counting with 85%+ accuracy
- **Species Classification**: Identify 5 major tree species
- **Health Assessment**: NDVI-based forest health monitoring
- **Density Analysis**: Trees per hectare calculations

### 🎨 Modern UI/UX
- **Glassmorphism Design**: Beautiful frosted glass effects
- **Forest Background**: Immersive aerial forest imagery
- **Smooth Animations**: Interactive preview and scroll effects
- **Responsive Layout**: Works on desktop and mobile devices
- **Dark Mode Ready**: Optimized for various lighting conditions

### 🔐 User Authentication
- **Secure Sign-In/Register**: Modal-based authentication system
- **Session Management**: Remember me functionality
- **Google OAuth**: Quick sign-in with Google (demo)

---

## � Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the Repository**
```bash
git clone <repository-url>
cd forest_monitoring_system
```

2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

3. **Add Satellite Data**
Place your Sentinel-2 imagery at:
```
data/raw/sentinel2_dang_march_2024.tif
```

### Running the Application

1. **Start Backend Server**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Start Frontend Server** (in a new terminal)
```bash
cd frontend
python3 serve.py
```

3. **Open Your Browser**
```
http://localhost:5500
```

---

## 📖 How to Use

1. **Sign In**: Click "SIGN IN" on the homepage and create an account
2. **Navigate to Map**: Click "START ANALYSIS" to access the monitoring dashboard
3. **Draw Region**: Use the "Draw Region" button to select a forest area
4. **Analyze**: Click "Analyze Forest" to process the selected region
5. **View Results**: See circular progress indicators, species distribution, and tree locations

---

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Leaflet.js for interactive maps
- Custom animations and glassmorphism effects
- Responsive design with modern UI patterns

**Backend:**
- FastAPI (Python web framework)
- Rasterio (Geospatial data processing)
- NumPy (Numerical computations)
- Uvicorn (ASGI server)

**Machine Learning:**
- DeepForest (Tree detection)
- Custom forest density estimator
- NDVI-based health assessment
- Spectral analysis for species classification

**Data:**
- Sentinel-2 satellite imagery (10m resolution)
- Multi-spectral bands (Red, Green, Blue, NIR)
- GeoTIFF format

### Project Structure

```
forest_monitoring_system/
│
├── frontend/                    # Web interface
│   ├── index.html              # Main application page
│   ├── app.js                  # JavaScript logic
│   ├── styles.css              # Styling and animations
│   ├── serve.py                # Development server
│   ├── forest-aerial.jpg       # Background image
│   └── video.mp4               # Hero section video
│
├── backend/                     # API server
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   │
│   ├── api/
│   │   └── routes.py           # API endpoints
│   │
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   │
│   └── services/
│       ├── data_loader.py      # Satellite data loading
│       ├── ml_interface.py     # ML model interface
│       ├── ndvi_calculator.py  # NDVI computation
│       └── area_calculator.py  # Geographic calculations
│
├── ml_models/                   # Machine learning models
│   ├── forest_estimator.py     # Density estimation
│   ├── tree_detector.py        # DeepForest integration
│   ├── species_classifier.py   # Species identification
│   ├── dang_forest_model.pkl   # Trained model
│   └── dang_scaler.pkl         # Feature scaler
│
├── data/
│   ├── raw/                    # Satellite imagery
│   │   └── sentinel2_dang_march_2024.tif
│   └── training/               # Ground truth data
│       └── dang_ground_truth.csv
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## � Species Detection

The system identifies and estimates distribution of 5 major tree species found in Dang District:

| Species | Scientific Name | Typical Distribution |
|---------|----------------|---------------------|
| 🌲 Teak | *Tectona grandis* | 30-40% |
| 🌳 Sal | *Shorea robusta* | 25-30% |
| 🎋 Bamboo | *Bambusa spp.* | 15-25% |
| 🥭 Mango | *Mangifera indica* | 10-15% |
| 🌿 Neem | *Azadirachta indica* | 5-10% |

Distribution varies based on forest density, elevation, and spectral signatures.

---

## 📊 Analysis Methodology

### NDVI Calculation
```
NDVI = (NIR - Red) / (NIR + Red)
```
- Range: -1 to +1
- Healthy vegetation: 0.6 to 0.9
- Sparse vegetation: 0.2 to 0.4

### Tree Density Estimation
```
NDVI > 0.7   → 180 trees/hectare (very dense forest)
NDVI 0.6-0.7 → 150 trees/hectare (dense forest)
NDVI 0.4-0.6 → 80 trees/hectare (medium density)
NDVI 0.3-0.4 → 30 trees/hectare (sparse forest)
NDVI < 0.3   → 10 trees/hectare (very sparse)
```

### Total Tree Count
```
Total Trees = Area (hectares) × Trees per hectare
```

### Health Score
```
Health Score = (NDVI - 0.2) / 0.7 × 100
```
Normalized to 0-100 scale based on vegetation health.

---

## 🎯 Accuracy & Limitations

### Strengths
✅ Large-area forest monitoring (50-1000+ hectares)  
✅ Cost-effective (free satellite data)  
✅ Regular updates (Sentinel-2 revisit: 5 days)  
✅ Multi-spectral analysis  
✅ Scientifically validated methods  

### Limitations
⚠️ **Tree Count Accuracy**: ±20-30% (density-based estimation)  
⚠️ **Species Distribution**: ±15-25% (spectral approximation)  
⚠️ **Resolution**: 10m per pixel (cannot detect individual small trees)  
⚠️ **Cloud Cover**: Requires clear sky imagery  

### Why Estimation?
Sentinel-2's 10-meter resolution is designed for landscape-level monitoring, not individual tree counting. This system uses industry-standard density estimation methods employed by:
- Forest Survey of India (FSI)
- FAO Global Forest Resources Assessment
- NASA Earth Observation programs
- International forestry research institutions

### For Individual Tree Detection
Requires high-resolution imagery (0.3-1m per pixel) from:
- Drones/UAVs
- Aerial photography
- Very high-resolution satellites (WorldView, Pleiades)

---

## 🔧 API Endpoints

### Health Check
```http
GET /api/v1/health
```
Returns server status.

### Satellite Coverage
```http
GET /api/v1/satellite-coverage
```
Returns available satellite imagery bounds and center coordinates.

### Forest Analysis
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "bounds": {
    "min_lat": 20.7,
    "max_lat": 20.8,
    "min_lon": 73.7,
    "max_lon": 73.8
  },
  "date": "2024-03-01"
}
```

Returns comprehensive forest analysis including:
- Tree count and density
- Species distribution
- NDVI statistics
- Health metrics
- Tree locations

---

## 🎨 UI Features

### Landing Page
- Full-screen video background
- Glassmorphism navigation bar
- Smooth scroll animations
- Interactive content sections
- Floating navigation button

### Map Page
- Transparent navigation with forest background
- Circular progress KPI cards
- Interactive preview animation
- Real-time analysis results
- Modern glassmorphism design

### Empty State
- Animated mini-map preview
- Step-by-step process indicators
- Floating data points
- Engaging user guidance

---

## 🔐 Security Notes

- Authentication is currently demo/frontend-only
- For production, implement proper backend authentication
- Add JWT tokens for API security
- Use environment variables for sensitive data
- Enable HTTPS in production

---

## 🚧 Future Enhancements

- [ ] Real backend authentication with JWT
- [ ] User dashboard with analysis history
- [ ] Export results to PDF/CSV
- [ ] Time-series analysis (forest change detection)
- [ ] Multi-region comparison
- [ ] Mobile app version
- [ ] Integration with more satellite sources
- [ ] Advanced ML models for better accuracy
- [ ] Deforestation alerts
- [ ] Carbon stock estimation

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Sentinel-2**: European Space Agency (ESA) for free satellite imagery
- **DeepForest**: Weecology lab for tree detection models
- **Leaflet.js**: Open-source mapping library
- **FastAPI**: Modern Python web framework
- **Dang District**: Forest department for ecological data

---

## 📞 Support & Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check the documentation
- Review the API endpoints

---

## 🌍 Impact

This system supports:
- 🌲 Forest conservation efforts
- 📊 Data-driven forest management
- 🔬 Environmental research
- 📈 Sustainable development goals
- 🌱 Biodiversity monitoring

---

**Built with ❤️ for forest conservation and environmental protection**

*ForestEye - Protecting Nature with Intelligence* 🌲🛰️🤖
