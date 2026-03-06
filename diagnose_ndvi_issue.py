"""
Diagnose why NDVI is showing 0.000
"""

import rasterio
import numpy as np

print("="*70)
print("Diagnosing NDVI Issue")
print("="*70)

# Test bounds from your screenshot (approximate)
test_bounds = {
    'min_lat': 20.6068,
    'min_lon': 73.6822,
    'max_lat': 20.6168,
    'max_lon': 73.6922
}

print(f"\nTest bounds:")
print(f"  Lat: {test_bounds['min_lat']} to {test_bounds['max_lat']}")
print(f"  Lon: {test_bounds['min_lon']} to {test_bounds['max_lon']}")

with rasterio.open('data/raw/sentinel2_dang_march_2024.tif') as src:
    print(f"\nSatellite file info:")
    print(f"  Bands: {src.count}")
    print(f"  Band names: {src.descriptions}")
    print(f"  Size: {src.width} x {src.height}")
    print(f"  CRS: {src.crs}")
    print(f"  Dtype: {src.dtypes}")
    
    # Get satellite bounds
    from rasterio.warp import transform_bounds
    sat_bounds = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
    print(f"\nSatellite coverage:")
    print(f"  Lat: {sat_bounds[1]:.4f} to {sat_bounds[3]:.4f}")
    print(f"  Lon: {sat_bounds[0]:.4f} to {sat_bounds[2]:.4f}")
    
    # Calculate pixel coordinates
    lat_fraction_min = (test_bounds['min_lat'] - sat_bounds[1]) / (sat_bounds[3] - sat_bounds[1])
    lat_fraction_max = (test_bounds['max_lat'] - sat_bounds[1]) / (sat_bounds[3] - sat_bounds[1])
    lon_fraction_min = (test_bounds['min_lon'] - sat_bounds[0]) / (sat_bounds[2] - sat_bounds[0])
    lon_fraction_max = (test_bounds['max_lon'] - sat_bounds[0]) / (sat_bounds[2] - sat_bounds[0])
    
    row_start = int((1 - lat_fraction_max) * src.height)
    row_end = int((1 - lat_fraction_min) * src.height)
    col_start = int(lon_fraction_min * src.width)
    col_end = int(lon_fraction_max * src.width)
    
    print(f"\nPixel coordinates:")
    print(f"  Rows: {row_start} to {row_end}")
    print(f"  Cols: {col_start} to {col_end}")
    
    # Read bands
    from rasterio.windows import Window
    window = Window(col_start, row_start, col_end - col_start, row_end - row_start)
    
    print(f"\nReading bands...")
    red = src.read(1, window=window).astype(float)
    green = src.read(2, window=window).astype(float)
    blue = src.read(3, window=window).astype(float)
    nir = src.read(4, window=window).astype(float)
    
    print(f"  Red shape: {red.shape}")
    print(f"  Green shape: {green.shape}")
    print(f"  Blue shape: {blue.shape}")
    print(f"  NIR shape: {nir.shape}")
    
    print(f"\nRaw values (before normalization):")
    print(f"  Red:   min={red.min():.0f}, max={red.max():.0f}, mean={red.mean():.0f}")
    print(f"  Green: min={green.min():.0f}, max={green.max():.0f}, mean={green.mean():.0f}")
    print(f"  Blue:  min={blue.min():.0f}, max={blue.max():.0f}, mean={blue.mean():.0f}")
    print(f"  NIR:   min={nir.min():.0f}, max={nir.max():.0f}, mean={nir.mean():.0f}")
    
    # Normalize
    if red.max() > 1.0:
        print(f"\nNormalizing by 10000...")
        red = red / 10000.0
        green = green / 10000.0
        blue = blue / 10000.0
        nir = nir / 10000.0
    
    print(f"\nNormalized values:")
    print(f"  Red:   min={red.min():.4f}, max={red.max():.4f}, mean={red.mean():.4f}")
    print(f"  Green: min={green.min():.4f}, max={green.max():.4f}, mean={green.mean():.4f}")
    print(f"  Blue:  min={blue.min():.4f}, max={blue.max():.4f}, mean={blue.mean():.4f}")
    print(f"  NIR:   min={nir.min():.4f}, max={nir.max():.4f}, mean={nir.mean():.4f}")
    
    # Calculate NDVI
    ndvi = (nir - red) / (nir + red + 1e-8)
    
    print(f"\nNDVI calculation:")
    print(f"  NDVI min: {ndvi.min():.4f}")
    print(f"  NDVI max: {ndvi.max():.4f}")
    print(f"  NDVI mean: {ndvi.mean():.4f}")
    print(f"  NDVI std: {ndvi.std():.4f}")
    
    if ndvi.mean() == 0.0:
        print(f"\n❌ PROBLEM FOUND: NDVI is 0!")
        print(f"   This means NIR and Red bands are equal or both zero")
        print(f"   Checking if bands contain data...")
        print(f"   Red non-zero pixels: {np.count_nonzero(red)}/{red.size}")
        print(f"   NIR non-zero pixels: {np.count_nonzero(nir)}/{nir.size}")
    else:
        print(f"\n✓ NDVI looks good!")

print("\n" + "="*70)
