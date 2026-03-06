from shapely.geometry import box
import geopandas as gpd
from backend.models.schemas import Bounds


class AreaCalculator:
    @staticmethod
    def calculate_hectares(bounds: Bounds) -> float:
        """
        Calculate area in hectares from lat/lon bounds
        
        Args:
            bounds: Bounds object with min/max lat/lon
        
        Returns:
            Area in hectares
        """
        # Create geometry
        geometry = box(
            bounds.min_lon,
            bounds.min_lat,
            bounds.max_lon,
            bounds.max_lat
        )
        
        # Create GeoDataFrame with WGS84 CRS
        gdf = gpd.GeoDataFrame([1], geometry=[geometry], crs='EPSG:4326')
        
        # Project to metric CRS (Web Mercator for approximate area)
        gdf_projected = gdf.to_crs('EPSG:3857')
        
        # Calculate area in square meters
        area_m2 = gdf_projected.geometry.area[0]
        
        # Convert to hectares (1 hectare = 10,000 m²)
        area_hectares = area_m2 / 10000
        
        return float(area_hectares)


area_calculator = AreaCalculator()
