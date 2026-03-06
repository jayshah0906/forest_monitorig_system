from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


# Request Models
class Bounds(BaseModel):
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)


class AnalysisRequest(BaseModel):
    bounds: Bounds
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')


# Response Models
class NDVIStats(BaseModel):
    mean: float
    std: float
    min: float
    max: float


class KPIs(BaseModel):
    tree_count: int
    tree_density: float
    area_hectares: float
    species_distribution: Dict[str, float]
    species_counts: Dict[str, int]
    ndvi: NDVIStats
    health_score: int
    health_status: str


class TreeLocation(BaseModel):
    lat: float
    lon: float
    species: str
    confidence: float


class NDVIHeatmap(BaseModel):
    data: List[List[float]]
    bounds: Bounds


class AnalysisData(BaseModel):
    kpis: KPIs
    tree_locations: List[TreeLocation]
    ndvi_heatmap: NDVIHeatmap


class AnalysisMetadata(BaseModel):
    processing_time: float
    timestamp: datetime


class AnalysisResponse(BaseModel):
    status: str
    data: Optional[AnalysisData] = None
    message: Optional[str] = None
    metadata: Optional[AnalysisMetadata] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


class DatesResponse(BaseModel):
    dates: List[str]


class BoundaryFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict
    properties: Dict


class BoundaryResponse(BaseModel):
    type: str = "FeatureCollection"
    features: List[BoundaryFeature]
