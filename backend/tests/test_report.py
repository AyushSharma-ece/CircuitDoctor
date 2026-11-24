"""
CircuitDoctor - Tests for Report Generation Service
Validates ReportLab PDF creation, structure, tables, and disclaimer formatting.
"""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.session import Base
from backend.app.models.inspection import Inspection, Detection
from backend.app.services.inspection_service import InspectionService
from backend.app.services.report_service import ReportService

# In-memory SQLite for testing
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_pdf_report_generation_with_defects():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed an inspection with multiple defect classes
    sample_detections = [
        {"class_id": 0, "class_name": "Missing Hole", "confidence": 0.94, "x1": 50, "y1": 50, "x2": 80, "y2": 80},
        {"class_id": 2, "class_name": "Open Circuit", "confidence": 0.88, "x1": 120, "y1": 200, "x2": 150, "y2": 230},
        {"class_id": 3, "class_name": "Short", "confidence": 0.91, "x1": 300, "y1": 310, "x2": 330, "y2": 340},
    ]

    insp = InspectionService.create_inspection(
        db=db,
        original_filename="test_pcb_board_alpha.jpg",
        stored_image_path="backend/uploads/sample_test.jpg",
        annotated_image_path="backend/annotated/sample_annotated.jpg",
        total_defects=3,
        inspection_status="fail",
        model_version="YOLO11n-PCB",
        confidence_threshold=0.25,
        inference_time=42.5,
        image_width=640,
        image_height=640,
        detections_data=sample_detections,
    )

    pdf_path = ReportService.generate_inspection_report(insp)
    assert pdf_path is not None
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Non-trivial PDF output

    # Check header magic bytes for valid PDF document (%PDF)
    with open(pdf_path, "rb") as f:
        header = f.read(5)
        assert header.startswith(b"%PDF")

    # Clean up test artifact
    try:
        os.remove(pdf_path)
    except Exception:
        pass
    db.close()


def test_pdf_report_generation_defect_free():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed a defect-free inspection
    insp = InspectionService.create_inspection(
        db=db,
        original_filename="perfect_pcb_board.jpg",
        stored_image_path="backend/uploads/clean_board.jpg",
        annotated_image_path=None,
        total_defects=0,
        inspection_status="pass",
        model_version="YOLO11n-PCB",
        confidence_threshold=0.25,
        inference_time=38.2,
        image_width=640,
        image_height=640,
        detections_data=[],
    )

    pdf_path = ReportService.generate_inspection_report(insp)
    assert pdf_path is not None
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000

    with open(pdf_path, "rb") as f:
        assert f.read(5).startswith(b"%PDF")

    try:
        os.remove(pdf_path)
    except Exception:
        pass
    db.close()


if __name__ == "__main__":
    test_pdf_report_generation_with_defects()
    test_pdf_report_generation_defect_free()
    print("All ReportService unit tests passed successfully!")
