"""
CircuitDoctor - Safe Image Streaming Endpoints
GET /api/images/original/{id}
GET /api/images/annotated/{id}
Serves inspection images with strict path validation.
"""

import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.inspection_service import InspectionService

router = APIRouter()

@router.get("/images/original/{inspection_id}")
def get_original_image(inspection_id: int, db: Session = Depends(get_db)):
    """Safely stream the original uploaded PCB image."""
    inspection = InspectionService.get_by_id(db, inspection_id)
    if not inspection or not inspection.stored_image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    file_path = Path(inspection.stored_image_path).resolve()
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File missing from storage")

    return FileResponse(file_path)

@router.get("/images/annotated/{inspection_id}")
def get_annotated_image(inspection_id: int, db: Session = Depends(get_db)):
    """Safely stream the AI-annotated PCB inspection image."""
    inspection = InspectionService.get_by_id(db, inspection_id)
    if not inspection or not inspection.annotated_image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotated image not found")

    file_path = Path(inspection.annotated_image_path).resolve()
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotated file missing from storage")

    return FileResponse(file_path)
