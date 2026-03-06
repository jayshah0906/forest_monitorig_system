# Sentinel-2 Satellite Data

## Required File
`sentinel2_dang_march_2024.tif` (110.94 MB)

## Why Not in GitHub?
This file exceeds GitHub's 100 MB file size limit and is not included in the repository.

## How to Get the Data

### Option 1: Use Your Local File
If you already have the file locally, keep it in this directory:
```
data/raw/sentinel2_dang_march_2024.tif
```

### Option 2: Download from Cloud Storage
Upload your file to:
- Google Drive
- Dropbox
- OneDrive
- Or any cloud storage

Then share the link with your team.

### Option 3: Use Alternative Sentinel-2 Data
Download Sentinel-2 data for Dang District from:
- **Copernicus Open Access Hub**: https://scihub.copernicus.eu/
- **Google Earth Engine**: https://earthengine.google.com/
- **USGS Earth Explorer**: https://earthexplorer.usgs.gov/

**Coordinates for Dang District:**
- Latitude: 20.50°N to 21.00°N
- Longitude: 73.50°E to 74.00°E
- Date: March 2024
- Bands needed: Red, Green, Blue, NIR (Near-Infrared)

## File Specifications
- **Format**: GeoTIFF (.tif)
- **Resolution**: 10m per pixel
- **Bands**: 4 (Red, Green, Blue, NIR)
- **Coverage**: Dang District, Gujarat
- **Size**: ~111 MB
- **Coordinate System**: WGS84 (EPSG:4326)

## For Demo
The system is fully functional with the local file. Make sure the file exists at:
```
data/raw/sentinel2_dang_march_2024.tif
```

Before running the demo, verify the file exists:
```bash
# Windows
dir data\raw\sentinel2_dang_march_2024.tif

# Linux/Mac
ls -lh data/raw/sentinel2_dang_march_2024.tif
```

## Note
The ML model and all other components are included in the repository. Only this large satellite data file needs to be obtained separately.
