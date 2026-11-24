"""
CircuitDoctor - Statistics Endpoint
GET /api/statistics
Calculates actual metrics, defect frequency, and latency averages from database records.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.inspection_service import InspectionService
from backend.app.schemas.inspection import StatisticsResponse
from backend.app.api.endpoints.health import check_model_status

router = APIRouter()

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """Return aggregated inspection analytics computed from live database entries."""
    model_status = check_model_status()
    return InspectionService.get_statistics(db, model_status=model_status)
