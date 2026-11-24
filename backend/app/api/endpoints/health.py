"""
CircuitDoctor - Health Check Endpoint
GET /api/health
Returns application runtime health, model availability status, and compute device.
"""

import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.database.session import get_db
from backend.app.schemas.inspection import HealthResponse

router = APIRouter()

def get_compute_device() -> str:
    """Detect available compute device (CUDA GPU vs CPU)."""
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

def check_model_status() -> str:
    """Inspect model file presence without loading weights."""
    if not settings.MODEL_PATH.exists():
        return "not_found"
    if settings.MODEL_PATH.stat().st_size < 1024:
        return "invalid"
    return "ready"

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint providing live system and model status."""
    # Test DB connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    model_status = check_model_status()
    device = get_compute_device()

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        project=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        model_status=model_status,
        model_path=str(settings.MODEL_PATH),
        device=device,
        database_status=db_status
    )
