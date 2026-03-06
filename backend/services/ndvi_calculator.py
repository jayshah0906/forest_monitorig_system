import numpy as np
from backend.models.schemas import NDVIStats


class NDVICalculator:
    @staticmethod
    def calculate(nir: np.ndarray, red: np.ndarray) -> tuple:
        """
        Calculate NDVI from NIR and Red bands
        
        Args:
            nir: Near-infrared band
            red: Red band
        
        Returns:
            tuple of (ndvi_array, ndvi_stats)
        """
        # Convert to float
        nir = nir.astype(float)
        red = red.astype(float)
        
        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        # Add small epsilon to avoid division by zero
        ndvi = (nir - red) / (nir + red + 1e-8)
        
        # Clip to valid range [-1, 1]
        ndvi = np.clip(ndvi, -1, 1)
        
        # Calculate statistics
        stats = NDVIStats(
            mean=float(np.mean(ndvi)),
            std=float(np.std(ndvi)),
            min=float(np.min(ndvi)),
            max=float(np.max(ndvi))
        )
        
        return ndvi, stats
    
    @staticmethod
    def calculate_health_score(ndvi_mean: float) -> tuple:
        """
        Convert NDVI to health score (0-100) and status
        
        Args:
            ndvi_mean: Mean NDVI value
        
        Returns:
            tuple of (health_score, health_status)
        """
        if ndvi_mean < 0.2:
            score = 20
            status = "Poor"
        elif ndvi_mean < 0.4:
            score = 50
            status = "Moderate"
        elif ndvi_mean < 0.6:
            score = 70
            status = "Good"
        else:
            # Scale 0.6-0.9 to 70-100
            score = min(100, int((ndvi_mean - 0.6) / 0.3 * 30 + 70))
            status = "Excellent" if score >= 80 else "Good"
        
        return score, status


ndvi_calculator = NDVICalculator()
