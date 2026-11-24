"""
CircuitDoctor - Inspection Service
Encapsulates database persistence, querying, deletion with file cleanup, and statistics aggregation.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.app.models.inspection import Inspection, Detection
from backend.app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionSummary,
    StatisticsResponse,
    DefectDistributionItem
)
from backend.app.core.defect_classes import DEFECT_CLASSES, get_class_name, get_class_info

class InspectionService:

    @staticmethod
    def get_by_id(db: Session, inspection_id: int) -> Optional[Inspection]:
        """Retrieve single inspection with its detections eagerly loaded."""
        return db.query(Inspection).filter(Inspection.id == inspection_id).first()

    @staticmethod
    def list_inspections(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        defect_class_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Inspection]:
        """List inspections with optional filtering and pagination."""
        query = db.query(Inspection)
        
        if status:
            query = query.filter(Inspection.inspection_status == status)
            
        if defect_class_id is not None:
            query = query.join(Inspection.detections).filter(Detection.class_id == defect_class_id).distinct()
            
        return query.order_by(desc(Inspection.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def create_inspection(
        db: Session,
        original_filename: str,
        stored_image_path: str,
        annotated_image_path: Optional[str],
        total_defects: int,
        inspection_status: str,
        model_version: str,
        confidence_threshold: float,
        inference_time: float,
        image_width: Optional[int] = None,
        image_height: Optional[int] = None,
        detections_data: Optional[List[Dict[str, Any]]] = None
    ) -> Inspection:
        """Create and persist an inspection record and associated defect detections."""
        inspection = Inspection(
            original_filename=original_filename,
            stored_image_path=stored_image_path,
            annotated_image_path=annotated_image_path,
            total_defects=total_defects,
            inspection_status=inspection_status,
            model_version=model_version,
            confidence_threshold=confidence_threshold,
            inference_time=inference_time,
            image_width=image_width,
            image_height=image_height
        )
        db.add(inspection)
        db.flush() # Populate inspection.id

        if detections_data:
            for det in detections_data:
                detection = Detection(
                    inspection_id=inspection.id,
                    class_id=det["class_id"],
                    class_name=det.get("class_name", get_class_name(det["class_id"])),
                    confidence=det["confidence"],
                    x1=det["x1"],
                    y1=det["y1"],
                    x2=det["x2"],
                    y2=det["y2"]
                )
                db.add(detection)

        db.commit()
        db.refresh(inspection)
        return inspection

    @staticmethod
    def delete_inspection(db: Session, inspection_id: int) -> bool:
        """Delete an inspection, its detections (cascade), and local image files."""
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            return False

        # Clean up disk files safely (prevent accidental deletion of dataset assets)
        for path_str in [inspection.stored_image_path, inspection.annotated_image_path]:
            if path_str and os.path.exists(path_str):
                # Safeguard: Never delete files from datasets directory
                if "datasets" in Path(path_str).parts:
                    continue
                try:
                    os.remove(path_str)
                except OSError:
                    pass

        db.delete(inspection)
        db.commit()
        return True

    @staticmethod
    def get_statistics(db: Session, model_status: str = "ready") -> StatisticsResponse:
        """Calculate real statistics from persisted inspection database records."""
        total_inspections = db.query(func.count(Inspection.id)).scalar() or 0
        total_defects = db.query(func.count(Detection.id)).scalar() or 0
        
        defect_free_count = db.query(func.count(Inspection.id)).filter(
            Inspection.total_defects == 0
        ).scalar() or 0
        
        defective_count = db.query(func.count(Inspection.id)).filter(
            Inspection.total_defects > 0
        ).scalar() or 0

        # Average inference time in milliseconds
        avg_time_sec = db.query(func.avg(Inspection.inference_time)).scalar() or 0.0
        avg_time_ms = round(float(avg_time_sec) * 1000.0, 2)

        # Defect class distribution
        class_counts_query = (
            db.query(Detection.class_id, func.count(Detection.id))
            .group_by(Detection.class_id)
            .all()
        )
        class_count_map = {row[0]: row[1] for row in class_counts_query}

        distribution_items: List[DefectDistributionItem] = []
        for cid, info in sorted(DEFECT_CLASSES.items()):
            count = class_count_map.get(cid, 0)
            percentage = round((count / total_defects * 100.0), 1) if total_defects > 0 else 0.0
            distribution_items.append(
                DefectDistributionItem(
                    class_id=cid,
                    class_name=info["name"],
                    count=count,
                    percentage=percentage,
                    color_hex=info["color_hex"],
                    severity=info["severity"]
                )
            )

        return StatisticsResponse(
            total_inspections=total_inspections,
            total_defects_detected=total_defects,
            total_images_inspected=total_inspections,
            defect_free_inspections=defect_free_count,
            defective_inspections=defective_count,
            average_inference_time_ms=avg_time_ms,
            defect_distribution=distribution_items,
            recent_inspections_count=min(total_inspections, 10),
            model_status=model_status
        )
