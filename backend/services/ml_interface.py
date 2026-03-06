import numpy as np
from typing import Dict
import sys
from pathlib import Path


class MLInterface:
    """
    Interface to ML models
    Uses forest density estimation for Sentinel-2 satellite imagery
    """
    
    def __init__(self):
        self.forest_estimator = None
        self.use_estimation = True  # Use estimation by default for Sentinel-2
        self._load_models()
    
    def _load_models(self):
        """Load forest estimation model"""
        try:
            # Add ml_models to path
            ml_models_path = Path("ml_models")
            if ml_models_path.exists():
                sys.path.insert(0, str(ml_models_path.absolute()))
            
            # Import forest estimator
            from forest_estimator import ForestEstimator
            
            self.forest_estimator = ForestEstimator()
            
            print("✓ Forest estimation model loaded successfully")
            print("✓ Using NDVI-based density estimation (optimized for Sentinel-2)")
        except Exception as e:
            print(f"⚠ Warning: Could not load forest estimator: {e}")
            raise
    
    def analyze(self, rgb_image: np.ndarray, nir_band: np.ndarray, 
                red_band: np.ndarray, bounds: Dict, area_hectares: float) -> Dict:
        """
        Estimate forest density and species distribution
        
        Args:
            rgb_image: RGB image array (H, W, 3)
            nir_band: NIR band array (H, W)
            red_band: Red band array (H, W)
            bounds: Bounds dict with min/max lat/lon
            area_hectares: Area in hectares
        
        Returns:
            dict with tree_detections and species_list
        """
        if not self.forest_estimator:
            raise RuntimeError(
                "Forest estimator not loaded! Cannot perform analysis."
            )
        
        print("Running forest density estimation (NDVI-based)")
        
        # Estimate forest characteristics
        estimation_result = self.forest_estimator.estimate_forest(
            rgb_image, nir_band, red_band, area_hectares
        )
        
        # Convert to expected format
        species_list = self._convert_to_species_list(
            estimation_result['tree_locations'],
            bounds
        )
        
        return {
            'tree_detections': estimation_result,
            'species_list': species_list
        }
    
    def _convert_to_species_list(self, tree_locations: list, bounds: Dict) -> list:
        """
        Convert tree locations to species list with lat/lon coordinates
        """
        species_list = []
        
        # Calculate lat/lon range
        lat_range = bounds['max_lat'] - bounds['min_lat']
        lon_range = bounds['max_lon'] - bounds['min_lon']
        
        for tree in tree_locations:
            # Convert pixel coordinates to lat/lon
            # Assuming uniform distribution
            lat_offset = (tree['pixel_y'] / 100.0) * lat_range  # Normalize by image size
            lon_offset = (tree['pixel_x'] / 100.0) * lon_range
            
            species_list.append({
                'species': tree['species'],
                'confidence': tree['confidence'],
                'lat': bounds['min_lat'] + lat_offset,
                'lon': bounds['min_lon'] + lon_offset
            })
        
        return species_list


ml_interface = MLInterface()
