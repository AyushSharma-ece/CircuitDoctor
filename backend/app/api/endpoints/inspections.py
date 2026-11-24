"""
CircuitDoctor - Inspections Management Endpoints
POST /api/inspect - Upload PCB image, run YOLO defect detection, persist results
GET /api/inspections - List previous inspection records
GET /api/inspections/{id} - Get complete inspection details
GET /api/inspections/{id}/report - Download generated PDF inspection report
DELETE /api/inspections/{id} - Delete record and image files
"""

import os
import time
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.services.inspection_service import InspectionService
from backend.app.services.detection_service import DetectionService
from backend.app.services.report_service import ReportService
from backend.app.schemas.inspection import InspectionResponse, InspectionSummary

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
UPLOADS_DIR = PROJECT_ROOT / "backend" / "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


def format_inspection_response(inspection) -> dict:
    """Format inspection model into serialized response with web image URLs."""
    data = {
        "id": inspection.id,
        "original_filename": inspection.original_filename,
        "stored_image_path": inspection.stored_image_path,
        "annotated_image_path": inspection.annotated_image_path,
        "total_defects": inspection.total_defects,
        "inspection_status": inspection.inspection_status,
        "model_version": inspection.model_version,
        "confidence_threshold": inspection.confidence_threshold,
        "inference_time": inspection.inference_time,
        "image_width": inspection.image_width,
        "image_height": inspection.image_height,
        "created_at": inspection.created_at,
        "original_image_url": f"/api/images/original/{inspection.id}",
        "annotated_image_url": f"/api/images/annotated/{inspection.id}" if inspection.annotated_image_path else None,
        "report_url": f"/api/inspections/{inspection.id}/report",
        "detections": [
            {
                "id": d.id,
                "inspection_id": d.inspection_id,
                "class_id": d.class_id,
                "class_name": d.class_name,
                "confidence": d.confidence,
                "x1": d.x1,
                "y1": d.y1,
                "x2": d.x2,
                "y2": d.y2
            }
            for d in inspection.detections
        ]
    }
    return data


@router.post("/inspect", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def inspect_pcb(
    file: UploadFile = File(...),
    confidence_threshold: float = Form(0.25),
    iou_threshold: float = Form(0.45),
    db: Session = Depends(get_db)
):
    """
    Upload a PCB image for automated defect detection:
    1. Validates file format and size limits.
    2. Saves raw image to persistent uploads storage.
    3. Executes YOLO deep learning inference.
    4. Generates color-coded annotated defect overlay.
    5. Persists inspection record and detection coordinates in SQLite.
    """
    # 1. Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Save uploaded file to disk
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time() * 1000)
    clean_stem = Path(file.filename).stem.replace(" ", "_")
    stored_filename = f"{timestamp}_{clean_stem}{file_ext}"
    stored_path = UPLOADS_DIR / stored_filename

    total_bytes = 0
    try:
        with open(stored_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size exceeds the maximum limit of 25 MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        if stored_path.exists():
            stored_path.unlink()
        raise
    except Exception as e:
        if stored_path.exists():
            stored_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # 3. Execute YOLO detection service
    detector = DetectionService.get_instance()
    try:
        detection_result = detector.detect(
            image_path=str(stored_path),
            conf_threshold=confidence_threshold,
            iou_threshold=iou_threshold,
            save_annotated=True
        )
    except Exception as e:
        if stored_path.exists():
            stored_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Neural inference error: {str(e)}"
        )

    # 4. Determine model version name
    model_name = "YOLO11n-PCB"
    if detector.model_path:
        model_name = Path(detector.model_path).name

    # 5. Persist inspection record in database
    try:
        inspection = InspectionService.create_inspection(
            db=db,
            original_filename=file.filename,
            stored_image_path=str(stored_path.resolve()),
            annotated_image_path=detection_result.get("annotated_image_path"),
            total_defects=detection_result["total_defects"],
            inspection_status=detection_result["visual_status"],
            model_version=model_name,
            confidence_threshold=confidence_threshold,
            inference_time=detection_result["inference_time_ms"],
            image_width=detection_result["image_width"],
            image_height=detection_result["image_height"],
            detections_data=detection_result["detections"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database persistence error: {str(e)}"
        )

    return format_inspection_response(inspection)


@router.get("/inspections", response_model=List[InspectionSummary])
def list_inspections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    defect_class: Optional[int] = Query(None, ge=0, le=5),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieve list of inspections with optional defect class and status filters."""
    filter_status = status if isinstance(status, str) else None
    filter_class = defect_class if isinstance(defect_class, int) else None
    skip_val = skip if isinstance(skip, int) else 0
    limit_val = limit if isinstance(limit, int) else 50

    inspections = InspectionService.list_inspections(
        db=db,
        skip=skip_val,
        limit=limit_val,
        defect_class_id=filter_class,
        status=filter_status
    )

    summaries: List[InspectionSummary] = []
    for insp in inspections:
        defect_counts = {}
        for d in insp.detections:
            defect_counts[d.class_name] = defect_counts.get(d.class_name, 0) + 1

        summaries.append(
            InspectionSummary(
                id=insp.id,
                original_filename=insp.original_filename,
                total_defects=insp.total_defects,
                inspection_status=insp.inspection_status,
                model_version=insp.model_version,
                confidence_threshold=insp.confidence_threshold,
                inference_time=insp.inference_time,
                created_at=insp.created_at,
                defect_counts=defect_counts,
                original_image_url=f"/api/images/original/{insp.id}",
                annotated_image_url=f"/api/images/annotated/{insp.id}" if insp.annotated_image_path else None
            )
        )
    return summaries


@router.get("/inspections/{inspection_id}", response_model=InspectionResponse)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """Retrieve detailed results of a specific inspection."""
    inspection = InspectionService.get_by_id(db, inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection with ID {inspection_id} not found."
        )
    return format_inspection_response(inspection)


@router.get("/inspections/{inspection_id}/report")
def download_inspection_report(inspection_id: int, db: Session = Depends(get_db)):
    """Generate and download a comprehensive PDF inspection report."""
    inspection = InspectionService.get_by_id(db, inspection_id)
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection with ID {inspection_id} not found."
        )

    try:
        pdf_path = ReportService.generate_inspection_report(inspection)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"CircuitDoctor_Inspection_{inspection_id}_Report.pdf"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate inspection PDF report: {str(e)}"
        )


@router.delete("/inspections/{inspection_id}", status_code=status.HTTP_200_OK)
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """Delete an inspection, all defect records, and remove stored image files."""
    success = InspectionService.delete_inspection(db, inspection_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection with ID {inspection_id} not found."
        )
    return {"status": "success", "message": f"Inspection {inspection_id} and associated assets deleted."}
