"""
Find areas in the satellite image that have valid data
"""

import rasterio
import numpy as np
from rasterio.warp import transform_bounds

print("="*70)
print("Finding Valid Data Areas in Satellite Image")
print("="*70)

with rasterio.open('data/raw/sentinel2_dang_march_2024.tif') as src:
    # Get bounds
    sat_bounds = transform_bounds(src.crs, 'EPSG:4326', *src.bounds)
    print(f"\nSatellite coverage:")
    print(f"  Lat: {sat_bounds[1]:.4f} to {sat_bounds[3]:.4f}")
    print(f"  Lon: {sat_bounds[0]:.4f} to {sat_bounds[2]:.4f}")
    
    # Read NIR band (band 4)
    print(f"\nReading NIR band...")
    nir = src.read(4)
    
    print(f"  Shape: {nir.shape}")
    print(f"  Total pixels: {nir.size:,}")
    print(f"  Non-zero pixels: {np.count_nonzero(nir):,}")
    print(f"  Coverage: {np.count_nonzero(nir)/nir.size*100:.1f}%")
    
    # Find where data exists
    print(f"\nFinding valid data regions...")
    valid_mask = nir > 0
    
    # Find rows and columns with data
    valid_rows = np.where(np.any(valid_mask, axis=1))[0]
    valid_cols = np.where(np.any(valid_mask, axis=0))[0]
    
    if len(valid_rows) > 0 and len(valid_cols) > 0:
        row_start = valid_rows[0]
        row_end = valid_rows[-1]
        col_start = valid_cols[0]
        col_end = valid_cols[-1]
        
        print(f"  Valid data region (pixels):")
        print(f"    Rows: {row_start} to {row_end}")
        print(f"    Cols: {col_start} to {col_end}")
        
        # Convert to lat/lon
        height, width = nir.shape
        
        # Calculate fractions
        lat_fraction_min = 1 - (row_end / height)
        lat_fraction_max = 1 - (row_start / height)
        lon_fraction_min = col_start / width
        lon_fraction_max = col_end / width
        
        # Convert to actual lat/lon
        lat_min = sat_bounds[1] + lat_fraction_min * (sat_bounds[3] - sat_bounds[1])
        lat_max = sat_bounds[1] + lat_fraction_max * (sat_bounds[3] - sat_bounds[1])
        lon_min = sat_bounds[0] + lon_fraction_min * (sat_bounds[2] - sat_bounds[0])
        lon_max = sat_bounds[0] + lon_fraction_max * (sat_bounds[2] - sat_bounds[0])
        
        print(f"\n  Valid data region (lat/lon):")
        print(f"    Lat: {lat_min:.4f} to {lat_max:.4f}")
        print(f"    Lon: {lon_min:.4f} to {lon_max:.4f}")
        
        # Find center of valid data
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        
        print(f"\n  Center of valid data:")
        print(f"    Lat: {center_lat:.4f}")
        print(f"    Lon: {center_lon:.4f}")
        
        # Suggest a good test polygon (0.01 degrees ~ 1km)
        test_lat_min = center_lat - 0.005
        test_lat_max = center_lat + 0.005
        test_lon_min = center_lon - 0.005
        test_lon_max = center_lon + 0.005
        
        print(f"\n{'='*70}")
        print(f"✓ RECOMMENDED TEST POLYGON:")
        print(f"{'='*70}")
        print(f"  Draw a polygon around these coordinates:")
        print(f"    Lat: {test_lat_min:.4f} to {test_lat_max:.4f}")
        print(f"    Lon: {test_lon_min:.4f} to {test_lon_max:.4f}")
        print(f"\n  Or use this center point: ({center_lat:.4f}, {center_lon:.4f})")
        print(f"  And draw a small polygon around it")
        print(f"{'='*70}")
        
        # Check a sample from this area
        print(f"\nVerifying data in recommended area...")
        test_row = int((1 - (center_lat - sat_bounds[1]) / (sat_bounds[3] - sat_bounds[1])) * height)
        test_col = int(((center_lon - sat_bounds[0]) / (sat_bounds[2] - sat_bounds[0])) * width)
        
        # Read small window
        from rasterio.windows import Window
        window = Window(test_col - 50, test_row - 50, 100, 100)
        
        red_sample = src.read(1, window=window)
        nir_sample = src.read(4, window=window)
        
        print(f"  Sample area (100x100 pixels):")
        print(f"    Red: min={red_sample.min()}, max={red_sample.max()}, mean={red_sample.mean():.0f}")
        print(f"    NIR: min={nir_sample.min()}, max={nir_sample.max()}, mean={nir_sample.mean():.0f}")
        
        if red_sample.mean() > 0 and nir_sample.mean() > 0:
            ndvi_sample = (nir_sample - red_sample) / (nir_sample + red_sample + 1e-8)
            print(f"    NDVI: mean={ndvi_sample.mean():.3f}")
            print(f"\n  ✓ This area has valid data!")
        else:
            print(f"\n  ⚠ Warning: Sample area might still have issues")
    
    else:
        print(f"  ❌ No valid data found in image!")

print("\n" + "="*70)
