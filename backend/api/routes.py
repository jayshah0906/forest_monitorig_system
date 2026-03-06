from fastapi import APIRouter, HTTPException
from datetime import datetime
import time
import numpy as np

from backend.models.schemas import (
    AnalysisRequest, AnalysisResponse, AnalysisData, AnalysisMetadata,
    HealthResponse, DatesResponse, BoundaryResponse,
    KPIs, TreeLocation, NDVIHeatmap
)
from backend.services.data_loader import data_loader
from backend.services.ndvi_calculator import ndvi_calculator
from backend.services.area_calculator import area_calculator
from backend.services.ml_interface import ml_interface

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now()
    )


@router.get("/dates", response_model=DatesResponse)
async def get_dates():
    """Get available dates for satellite imagery"""
    dates = data_loader.get_available_dates()
    return DatesResponse(dates=dates)


@router.get("/boundary", response_model=BoundaryResponse)
async def get_boundary():
    """Get forest boundary as GeoJSON"""
    try:
        boundary = data_loader.load_forest_boundary()
        return boundary
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load boundary: {str(e)}"
        )


@router.get("/satellite-coverage")
async def get_satellite_coverage():
    """Get the coverage area of the satellite image"""
    try:
        import rasterio
        from rasterio.warp import transform_bounds
        
        with rasterio.open(data_loader.sentinel_path) as src:
            # Transform bounds to lat/lon
            bounds = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
            
            # Calculate center
            center_lat = (bounds[1] + bounds[3]) / 2
            center_lon = (bounds[0] + bounds[2]) / 2
            
            return {
                "bounds": {
                    "min_lon": bounds[0],
                    "min_lat": bounds[1],
                    "max_lon": bounds[2],
                    "max_lat": bounds[3]
                },
                "center": {
                    "lat": center_lat,
                    "lon": center_lon
                },
                "message": "Draw your polygon within these bounds"
            }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Satellite image not found. Please add sentinel2_dang_march_2024.tif to data/raw/"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get coverage: {str(e)}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_forest(request: AnalysisRequest):
    """
    Main analysis endpoint
    
    Analyzes forest area and returns:
    - Tree count and density
    - Species distribution
    - NDVI and health metrics
    - Tree locations
    - NDVI heatmap
    """
    start_time = time.time()
    
    try:
        print(f"\n{'='*60}")
        print(f"Starting forest analysis...")
        print(f"Bounds: {request.bounds}")
        print(f"Date: {request.date}")
        print(f"{'='*60}\n")
        
        # 1. Load satellite data
        print("Step 1: Loading satellite data...")
        data = data_loader.load_satellite_image(request.bounds)
        rgb_image = data['rgb_image']
        nir_band = data['nir_band']
        red_band = data['red_band']
        print(f"✓ Loaded image shape: {rgb_image.shape}")
        
        # 2. Calculate NDVI
        print("\nStep 2: Calculating NDVI...")
        ndvi, ndvi_stats = ndvi_calculator.calculate(nir_band, red_band)
        print(f"✓ NDVI mean: {ndvi_stats.mean:.3f}")
        
        # 3. Calculate area
        print("\nStep 3: Calculating area...")
        area_hectares = area_calculator.calculate_hectares(request.bounds)
        print(f"✓ Area: {area_hectares:.2f} hectares")
        
        # 4. Run ML analysis
        print("\nStep 4: Running ML analysis...")
        ml_results = ml_interface.analyze(
            rgb_image, 
            nir_band, 
            red_band,
            request.bounds.dict(),
            area_hectares  # Pass area for density estimation
        )
        print(f"✓ Estimated {len(ml_results['species_list'])} trees")
        
        # 5. Calculate KPIs
        print("\nStep 5: Calculating KPIs...")
        tree_count = len(ml_results['species_list'])
        tree_density = tree_count / area_hectares if area_hectares > 0 else 0
        
        # Species distribution
        species_counts = {}
        for tree in ml_results['species_list']:
            species = tree['species']
            species_counts[species] = species_counts.get(species, 0) + 1
        
        species_distribution = {}
        if tree_count > 0:
            for species, count in species_counts.items():
                species_distribution[species] = round((count / tree_count) * 100, 1)
        
        # Health score
        health_score, health_status = ndvi_calculator.calculate_health_score(
            ndvi_stats.mean
        )
        
        print(f"✓ Tree density: {tree_density:.2f} trees/ha")
        print(f"✓ Health score: {health_score}/100 ({health_status})")
        print(f"✓ Species: {list(species_counts.keys())}")
        
        # 6. Prepare response
        print("\nStep 6: Preparing response...")
        
        kpis = KPIs(
            tree_count=tree_count,
            tree_density=round(tree_density, 2),
            area_hectares=round(area_hectares, 2),
            species_distribution=species_distribution,
            species_counts=species_counts,
            ndvi=ndvi_stats,
            health_score=health_score,
            health_status=health_status
        )
        
        # Tree locations (limit to 200 for performance)
        tree_locations = [
            TreeLocation(**tree) 
            for tree in ml_results['species_list'][:200]
        ]
        
        # NDVI heatmap (downsample for performance)
        # Take every 10th pixel to reduce data size
        ndvi_downsampled = ndvi[::10, ::10]
        ndvi_heatmap = NDVIHeatmap(
            data=ndvi_downsampled.tolist(),
            bounds=request.bounds
        )
        
        analysis_data = AnalysisData(
            kpis=kpis,
            tree_locations=tree_locations,
            ndvi_heatmap=ndvi_heatmap
        )
        
        processing_time = time.time() - start_time
        
        print(f"\n{'='*60}")
        print(f"✓ Analysis complete in {processing_time:.2f} seconds")
        print(f"{'='*60}\n")
        
        return AnalysisResponse(
            status="success",
            data=analysis_data,
            metadata=AnalysisMetadata(
                processing_time=round(processing_time, 2),
                timestamp=datetime.now()
            )
        )
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/report")
async def download_report(analysis_id: str):
    """Download analysis report as CSV"""
    # TODO: Implement report generation
    raise HTTPException(
        status_code=501,
        detail="Report download not implemented yet"
    )
