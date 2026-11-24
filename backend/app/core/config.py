"""
CircuitDoctor - Application Configuration
Type-safe environment configuration with robust defaults.
"""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_ROOT = BASE_DIR.parent

class Settings(BaseModel):
    PROJECT_NAME: str = "CircuitDoctor"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Network
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Storage Paths
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'circuitdoctor.db'}")
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ANNOTATED_DIR: Path = BASE_DIR / "annotated"
    REPORTS_DIR: Path = WORKSPACE_ROOT / "reports"
    MODELS_DIR: Path = WORKSPACE_ROOT / "models"
    MODEL_PATH: Path = WORKSPACE_ROOT / "models" / "best.pt"
    
    # Inference parameters
    DEFAULT_CONFIDENCE_THRESHOLD: float = float(os.getenv("DEFAULT_CONFIDENCE_THRESHOLD", "0.25"))
    DEFAULT_IOU_THRESHOLD: float = float(os.getenv("DEFAULT_IOU_THRESHOLD", "0.45"))
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "25"))
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png"]
    
    # Model Metadata
    MODEL_NAME: str = "CircuitDoctor-YOLO"
    MODEL_ARCHITECTURE: str = "Ultralytics YOLO26n"
    MODEL_TARGET_CLASSES: int = 6

settings = Settings()

# Ensure critical local directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
