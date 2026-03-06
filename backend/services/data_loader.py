import rasterio
from rasterio.windows import Window
import geopandas as gpd
import numpy as np
from pathlib import Path
from backend.config import settings
from backend.models.schemas import Bounds


class DataLoader:
    def __init__(self):
        self.sentinel_path = settings.RAW_DATA_DIR / "sentinel2_dang_march_2024.tif"
        self.boundary_path = settings.BOUNDARIES_DIR / "dang_forest_boundary.shp"
    
    def load_satellite_image(self, bounds: Bounds) -> dict:
        """
        Load REAL satellite image for selected bounds
        NO MOCK DATA - requires actual satellite imagery
        
        Returns:
            dict with rgb_image, nir_band, red_band, transform
        """
        # Check if file exists
        if not self.sentinel_path.exists():
            raise FileNotFoundError(
                f"\n{'='*60}\n"
                f"❌ SATELLITE IMAGERY NOT FOUND!\n"
                f"{'='*60}\n"
                f"Expected file: {self.sentinel_path}\n\n"
                f"📥 TO USE THIS SYSTEM, YOU NEED REAL SATELLITE DATA:\n\n"
                f"OPTION 1: Sentinel-2 (Recommended - FREE)\n"
                f"  1. Go to: https://scihub.copernicus.eu/\n"
                f"  2. Register for free account\n"
                f"  3. Search: Dang District, Gujarat (20.7°N, 73.7°E)\n"
                f"  4. Download: Sentinel-2 Level-2A (Surface Reflectance)\n"
                f"  5. Extract and place GeoTIFF at:\n"
                f"     data/raw/sentinel2_dang_march_2024.tif\n\n"
                f"OPTION 2: Google Earth Engine (FREE)\n"
                f"  1. Go to: https://code.earthengine.google.com/\n"
                f"  2. Export Sentinel-2 for Dang District\n\n"
                f"OPTION 3: USGS Earth Explorer (FREE)\n"
                f"  1. Go to: https://earthexplorer.usgs.gov/\n"
                f"  2. Search: Dang, Gujarat, India\n"
                f"  3. Download: Landsat 8 or Sentinel-2\n\n"
                f"📋 FILE REQUIREMENTS:\n"
                f"  - Format: GeoTIFF (.tif)\n"
                f"  - Bands: Red, Green, Blue, NIR (in that order)\n"
                f"  - Resolution: 10m (Sentinel-2) or 30m (Landsat)\n"
                f"  - Coverage: Dang District area\n\n"
                f"After adding the file, restart the backend:\n"
                f"  python run_backend.py\n"
                f"{'='*60}\n"
            )
        
        print(f"Loading real satellite imagery from: {self.sentinel_path}")
        
        with rasterio.open(self.sentinel_path) as src:
            print(f"✓ File opened successfully")
            print(f"  - Bands: {src.count}")
            print(f"  - Size: {src.width} x {src.height}")
            print(f"  - CRS: {src.crs}")
            
            # Get satellite image bounds in lat/lon
            from rasterio.warp import transform_bounds
            sat_bounds = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
            print(f"  - Satellite coverage (lat/lon):")
            print(f"    Lat: {sat_bounds[1]:.4f} to {sat_bounds[3]:.4f}")
            print(f"    Lon: {sat_bounds[0]:.4f} to {sat_bounds[2]:.4f}")
            
            # Check if requested bounds are within satellite coverage
            if (bounds.min_lon < sat_bounds[0] or bounds.max_lon > sat_bounds[2] or
                bounds.min_lat < sat_bounds[1] or bounds.max_lat > sat_bounds[3]):
                raise ValueError(
                    f"\n{'='*60}\n"
                    f"❌ SELECTED AREA IS OUTSIDE SATELLITE COVERAGE!\n"
                    f"{'='*60}\n"
                    f"Your selected area:\n"
                    f"  Lat: {bounds.min_lat:.4f} to {bounds.max_lat:.4f}\n"
                    f"  Lon: {bounds.min_lon:.4f} to {bounds.max_lon:.4f}\n\n"
                    f"Satellite image covers:\n"
                    f"  Lat: {sat_bounds[1]:.4f} to {sat_bounds[3]:.4f}\n"
                    f"  Lon: {sat_bounds[0]:.4f} to {sat_bounds[2]:.4f}\n\n"
                    f"Please draw your polygon inside the green box on the map.\n"
                    f"{'='*60}\n"
                )
            
            print(f"  - Using manual pixel coordinate calculation (bypassing broken transform)")
            
            # Manual calculation: convert lat/lon to pixel coordinates
            # Calculate the fraction of the image for the selected bounds
            lat_fraction_min = (bounds.min_lat - sat_bounds[1]) / (sat_bounds[3] - sat_bounds[1])
            lat_fraction_max = (bounds.max_lat - sat_bounds[1]) / (sat_bounds[3] - sat_bounds[1])
            lon_fraction_min = (bounds.min_lon - sat_bounds[0]) / (sat_bounds[2] - sat_bounds[0])
            lon_fraction_max = (bounds.max_lon - sat_bounds[0]) / (sat_bounds[2] - sat_bounds[0])
            
            # Convert to pixel coordinates (note: row is inverted for latitude)
            row_start = int((1 - lat_fraction_max) * src.height)
            row_end = int((1 - lat_fraction_min) * src.height)
            col_start = int(lon_fraction_min * src.width)
            col_end = int(lon_fraction_max * src.width)
            
            # Ensure valid ranges
            row_start = max(0, min(row_start, src.height - 1))
            row_end = max(row_start + 1, min(row_end, src.height))
            col_start = max(0, min(col_start, src.width - 1))
            col_end = max(col_start + 1, min(col_end, src.width))
            
            print(f"  - Pixel coordinates:")
            print(f"    Rows: {row_start} to {row_end} (height: {row_end - row_start})")
            print(f"    Cols: {col_start} to {col_end} (width: {col_end - col_start})")
            
            # Read bands using pixel coordinates
            from rasterio.windows import Window
            window = Window(col_start, row_start, col_end - col_start, row_end - row_start)
            
            print(f"  - Reading data from window: {window}")
            
            # Read bands (assuming band order: Red(1), Green(2), Blue(3), NIR(4))
            red = src.read(1, window=window).astype(float)
            green = src.read(2, window=window).astype(float)
            blue = src.read(3, window=window).astype(float)
            nir = src.read(4, window=window).astype(float)
            
            print(f"  - Read data shapes: R={red.shape}, G={green.shape}, B={blue.shape}, NIR={nir.shape}")
            
            # Check if we got any data
            if red.size == 0 or green.size == 0 or blue.size == 0 or nir.size == 0:
                raise ValueError(
                    "No data in selected area. The satellite image doesn't cover this region."
                )
            
            # Normalize to 0-1 range if needed (Sentinel-2 values are 0-10000)
            if red.max() > 1.0:
                print(f"  - Normalizing values (max: {red.max():.0f})")
                red = red / 10000.0
                green = green / 10000.0
                blue = blue / 10000.0
                nir = nir / 10000.0
            
            # Create RGB image (H, W, 3)
            rgb_image = np.stack([red, green, blue], axis=-1)
            
            # Get transform for the window
            transform = src.window_transform(window)
            
            print(f"✓ Loaded REAL satellite image: {rgb_image.shape}")
            print(f"  - Value ranges:")
            print(f"    Red:   {red.min():.3f} - {red.max():.3f}")
            print(f"    Green: {green.min():.3f} - {green.max():.3f}")
            print(f"    Blue:  {blue.min():.3f} - {blue.max():.3f}")
            print(f"    NIR:   {nir.min():.3f} - {nir.max():.3f}")
            
            return {
                'rgb_image': rgb_image,
                'nir_band': nir,
                'red_band': red,
                'transform': transform,
                'bounds': bounds
            }
    
    def load_forest_boundary(self) -> dict:
        """Load forest boundary as GeoJSON"""
        try:
            gdf = gpd.read_file(self.boundary_path)
            geojson = gdf.__geo_interface__
            return geojson
        except FileNotFoundError:
            print(f"Warning: Boundary file not found at {self.boundary_path}")
            print("Using default Dang district boundary")
            return self._generate_default_boundary()
    
    def _generate_default_boundary(self) -> dict:
        """Generate default boundary for Dang district"""
        # Approximate Dang district boundary
        return {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [73.5, 20.5],
                        [74.0, 20.5],
                        [74.0, 21.0],
                        [73.5, 21.0],
                        [73.5, 20.5]
                    ]]
                },
                "properties": {
                    "name": "Dang Forest",
                    "district": "Dang",
                    "state": "Gujarat"
                }
            }]
        }
    
    def get_available_dates(self) -> list:
        """Get list of available dates"""
        # In production, scan directory for available files
        # For now, return hardcoded dates
        return ["2024-03", "2024-02", "2024-01", "2023-12", "2023-11"]


data_loader = DataLoader()
