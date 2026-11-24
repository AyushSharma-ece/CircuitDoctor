"""
CircuitDoctor - Backend API and Service Test Suite
Directly tests endpoints, models, database persistence, and statistics.
"""

import pytest
from backend.app.main import root
from backend.app.database.session import SessionLocal, Base, engine
from backend.app.api.endpoints.health import health_check
from backend.app.api.endpoints.model import get_model_info
from backend.app.api.endpoints.stats import get_statistics
from backend.app.api.endpoints.inspections import list_inspections, get_inspection, delete_inspection
from backend.app.services.inspection_service import InspectionService
from backend.app.core.defect_classes import DEFECT_CLASSES

@pytest.fixture(scope="module")
def db_session():
    """Ensure database schema is created and yield a test session."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_root_endpoint():
    """Verify root endpoint returns project identity and engineering disclaimer."""
    result = root()
    assert result["project"] == "CircuitDoctor"
    assert result["version"] == "1.0.0"
    assert "limitation_notice" in result
    assert "electrical" in result["limitation_notice"].lower()

def test_health_check_endpoint(db_session):
    """Verify health endpoint reports correct database and model status."""
    health = health_check(db=db_session)
    assert health.status in ["healthy", "degraded"]
    assert health.project == "CircuitDoctor"
    assert health.database_status == "connected"
    assert health.model_status in ["ready", "not_found", "invalid"]
    assert health.device in ["cpu", "cuda"]

def test_model_info_endpoint():
    """Verify model metadata returns exact DeepPCB defect categories."""
    info = get_model_info()
    assert info.model_name == "CircuitDoctor-YOLO"
    assert "YOLO26n" in info.model_architecture
    assert len(info.supported_classes) == 6
    
    expected_classes = {
        0: "Missing Hole",
        1: "Mouse Bite",
        2: "Open Circuit",
        3: "Short",
        4: "Spur",
        5: "Spurious Copper"
    }
    for c in info.supported_classes:
        assert c.id in expected_classes
        assert c.name == expected_classes[c.id]
        assert c.severity in ["low", "medium", "high", "critical"]
        assert len(c.electrical_risk) > 0
        assert len(c.verification_advice) > 0

def test_statistics_endpoint_calculation(db_session):
    """Verify statistics aggregates metrics across real database records."""
    stats = get_statistics(db=db_session)
    assert stats.total_inspections >= 0
    assert stats.total_defects_detected >= 0
    assert len(stats.defect_distribution) == 6
    
    # Class IDs 0 to 5 must be present in the distribution
    distribution_ids = [d.class_id for d in stats.defect_distribution]
    assert distribution_ids == [0, 1, 2, 3, 4, 5]

def test_inspection_lifecycle_service(db_session):
    """Verify complete CRUD lifecycle: create, list, retrieve, cascade delete."""
    # 1. Create record with two defect detections
    created = InspectionService.create_inspection(
        db=db_session,
        original_filename="sample_layer1.png",
        stored_image_path="backend/uploads/sample_layer1.png",
        annotated_image_path=None,
        total_defects=2,
        inspection_status="completed",
        model_version="YOLO26n-v1.0",
        confidence_threshold=0.25,
        inference_time=0.032,
        image_width=640,
        image_height=640,
        detections_data=[
            {
                "class_id": 0,
                "confidence": 0.89,
                "x1": 45.0, "y1": 50.0, "x2": 85.0, "y2": 90.0
            },
            {
                "class_id": 2,
                "confidence": 0.78,
                "x1": 150.0, "y1": 200.0, "x2": 190.0, "y2": 240.0
            }
        ]
    )
    assert created.id is not None
    insp_id = created.id

    # 2. Retrieve via service
    fetched = InspectionService.get_by_id(db_session, insp_id)
    assert fetched is not None
    assert fetched.original_filename == "sample_layer1.png"
    assert len(fetched.detections) == 2
    assert fetched.detections[0].class_name == "Missing Hole"
    assert fetched.detections[1].class_name == "Open Circuit"

    # 3. Retrieve via endpoint
    endpoint_data = get_inspection(insp_id, db=db_session)
    assert endpoint_data["id"] == insp_id
    assert len(endpoint_data["detections"]) == 2

    # 4. Check listing endpoint
    summaries = list_inspections(skip=0, limit=10, db=db_session)
    assert any(s.id == insp_id for s in summaries)

    # 5. Delete record and verify cascade
    deleted = InspectionService.delete_inspection(db_session, insp_id)
    assert deleted is True

    # 6. Verify record is gone
    post_delete = InspectionService.get_by_id(db_session, insp_id)
    assert post_delete is None
