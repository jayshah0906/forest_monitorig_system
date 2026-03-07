from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import json


class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ForestEye API"
    VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:3001", "http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8080", "file://"]'
    
    # Data Paths
    DATA_DIR: Path = Path("data")
    RAW_DATA_DIR: Path = Path("data/raw")
    PROCESSED_DATA_DIR: Path = Path("data/processed")
    BOUNDARIES_DIR: Path = Path("data/boundaries")
    
    # ML Models
    ML_MODELS_DIR: Path = Path("ml_models")
    
    # Cache
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from string"""
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except:
            return ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
