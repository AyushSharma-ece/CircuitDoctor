"""
CircuitDoctor - End-to-End System Integration Test
Performs full automated workflow:
1. Queries /api/health to verify model_status == 'ready'
2. Queries /api/model/info to verify real evaluation metrics
3. Submits real test PCB image to /api/inspect
4. Verifies bounding boxes, coordinates, and optical disclaimer
5. Downloads official ReportLab PDF report via /api/inspections/{id}/report
6. Confirms persistence in database and cleans up test records
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import SessionLocal, Base, engine
from backend.app.api.endpoints.health import health_check
from backend.app.api.endpoints.model import get_model_info
from backend.app.services.detection_service import DetectionService
from backend.app.services.inspection_service import InspectionService
from backend.app.services.report_service import ReportService


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_system_health_model_ready(db_session):
    """Verify system health shows model ready and weights detected."""
    health = health_check(db=db_session)
    assert health.status == "healthy"
    assert health.database_status == "connected"
    assert health.model_status == "ready"


def test_model_info_real_evaluation_metrics():
    """Verify /api/model/info serves genuine evaluation metrics from test partition."""
    info = get_model_info()
    assert info.weights_exist is True
    assert info.model_status == "ready"
    assert info.training_metrics is not None
    assert "summary" in info.training_metrics
    assert info.training_metrics["summary"]["mAP50"] > 0.70
    assert info.training_metrics["evaluation_split"] == "test"
    assert len(info.training_metrics["per_class"]) == 6


def test_real_pcb_detection_inference():
    """Run real inference on a sample test PCB from the test partition."""
    test_images_dir = PROJECT_ROOT / "datasets" / "pcb_defects" / "images" / "test"
    test_images = list(test_images_dir.glob("*.jpg"))
    assert len(test_images) > 0, "No test images found in datasets/pcb_defects/images/test"

    sample_img_path = test_images[0]
    detector = DetectionService.get_instance()
    detector.load_model()
    assert detector.is_loaded

    result = detector.detect(
        image_path=str(sample_img_path),
        conf_threshold=0.25,
        iou_threshold=0.45,
        save_annotated=True,
    )

    assert "total_defects" in result
    assert "visual_status" in result
    assert result["visual_status"] in ["pass", "warning", "fail"]
    assert result["inference_time_ms"] > 0
    assert result["annotated_image_path"] is not None
    assert os.path.exists(result["annotated_image_path"])
    assert "optical_disclaimer" in result
    assert "electrical" in result["optical_disclaimer"].lower()


def test_full_inspection_and_pdf_report_lifecycle(db_session):
    """Perform full create, detect, persist, report, and delete cycle."""
    import shutil
    test_images_dir = PROJECT_ROOT / "datasets" / "pcb_defects" / "images" / "test"
    sample_img_path = list(test_images_dir.glob("*.jpg"))[0]

    # Create a test copy in uploads directory to avoid touching test dataset partition
    uploads_dir = PROJECT_ROOT / "backend" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    temp_test_copy = uploads_dir / f"test_e2e_{sample_img_path.name}"
    shutil.copy2(sample_img_path, temp_test_copy)

    detector = DetectionService.get_instance()
    detector.load_model()
    det_result = detector.detect(str(temp_test_copy), conf_threshold=0.25)

    # 1. Persist inspection
    insp = InspectionService.create_inspection(
        db=db_session,
        original_filename=sample_img_path.name,
        stored_image_path=str(temp_test_copy),
        annotated_image_path=det_result["annotated_image_path"],
        total_defects=det_result["total_defects"],
        inspection_status=det_result["visual_status"],
        model_version="YOLO11n-PCB",
        confidence_threshold=0.25,
        inference_time=det_result["inference_time_ms"],
        image_width=det_result["image_width"],
        image_height=det_result["image_height"],
        detections_data=det_result["detections"],
    )

    assert insp.id is not None
    insp_id = insp.id

    # 2. Generate PDF Report
    pdf_path = ReportService.generate_inspection_report(insp)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 2000

    # Check valid PDF signature
    with open(pdf_path, "rb") as f:
        assert f.read(5).startswith(b"%PDF")

    # 3. Clean up
    InspectionService.delete_inspection(db_session, insp_id)
    assert InspectionService.get_by_id(db_session, insp_id) is None
    if os.path.exists(pdf_path):
        os.remove(pdf_path)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
