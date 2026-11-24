"""
CircuitDoctor - Dataset Engineering Unit & Integration Tests
Validates coordinate conversion, class mapping, zero data leakage,
YOLO configuration integrity, and the dataset API endpoint.
"""

from pathlib import Path
import pytest
import yaml

from ml.dataset.converter import (
    convert_box_to_yolo,
    parse_deeppcb_annotation_line,
    DEEPPCB_RAW_TO_YOLO
)
from backend.app.core.defect_classes import DEFECT_CLASSES
from backend.app.api.endpoints.dataset import get_dataset_info

BASE_DIR = Path(__file__).resolve().parent.parent.parent
YAML_CONFIG = BASE_DIR / "ml" / "configs" / "pcb_defects.yaml"
DATASET_DIR = BASE_DIR / "datasets" / "pcb_defects"

def test_coordinate_conversion():
    """Verify conversion from absolute corners to normalized YOLO center/size."""
    # Centered box: (100, 100, 200, 200) on 640x640
    # cx = 150/640 = 0.234375, cy = 150/640 = 0.234375, w = 100/640 = 0.15625, h = 100/640 = 0.15625
    cx, cy, w, h = convert_box_to_yolo(100, 100, 200, 200, img_w=640, img_h=640)
    assert abs(cx - 0.234375) < 1e-4
    assert abs(cy - 0.234375) < 1e-4
    assert abs(w - 0.15625) < 1e-4
    assert abs(h - 0.15625) < 1e-4

    # Boundary box with slight overflow clamped
    cx2, cy2, w2, h2 = convert_box_to_yolo(0, 0, 700, 700, img_w=640, img_h=640)
    assert 0.0 <= cx2 <= 1.0
    assert 0.0 <= cy2 <= 1.0
    assert w2 <= 1.0
    assert h2 <= 1.0

def test_class_mapping_bijective():
    """Verify that all 6 DeepPCB raw classes (1-6) map uniquely to CircuitDoctor IDs (0-5)."""
    assert len(DEEPPCB_RAW_TO_YOLO) == 6
    mapped_ids = set(DEEPPCB_RAW_TO_YOLO.values())
    assert mapped_ids == {0, 1, 2, 3, 4, 5}

    # Verify pin-hole (6) maps to Missing Hole (0)
    assert DEEPPCB_RAW_TO_YOLO[6] == 0
    # Verify open (1) maps to Open Circuit (2)
    assert DEEPPCB_RAW_TO_YOLO[1] == 2
    # Verify short (2) maps to Short (3)
    assert DEEPPCB_RAW_TO_YOLO[2] == 3

def test_annotation_line_parsing():
    """Verify single line parsing from original DeepPCB format."""
    line = "466 441 493 470 3" # Raw class 3 = mousebite -> YOLO class 1
    parsed = parse_deeppcb_annotation_line(line, img_w=640, img_h=640)
    assert parsed is not None
    cid, cx, cy, w, h = parsed
    assert cid == 1  # Mouse Bite
    assert 0.0 < cx < 1.0
    assert 0.0 < cy < 1.0

def test_yolo_config_exists_and_valid():
    """Verify generated YOLO configuration file."""
    assert YAML_CONFIG.exists()
    with open(YAML_CONFIG, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["nc"] == 6
    assert "train" in data
    assert "val" in data
    assert "test" in data
    assert len(data["names"]) == 6

def test_zero_data_leakage():
    """Verify that train, val, and test splits have completely disjoint image sets."""
    train_imgs = {p.stem for p in (DATASET_DIR / "images" / "train").glob("*.jpg")}
    val_imgs = {p.stem for p in (DATASET_DIR / "images" / "val").glob("*.jpg")}
    test_imgs = {p.stem for p in (DATASET_DIR / "images" / "test").glob("*.jpg")}

    assert len(train_imgs) > 0
    assert len(val_imgs) > 0
    assert len(test_imgs) > 0

    assert len(train_imgs.intersection(val_imgs)) == 0, "Leakage detected between train and val!"
    assert len(train_imgs.intersection(test_imgs)) == 0, "Leakage detected between train and test!"
    assert len(val_imgs.intersection(test_imgs)) == 0, "Leakage detected between val and test!"

def test_dataset_info_api_endpoint():
    """Verify GET /api/dataset/info returns real metadata."""
    info = get_dataset_info()
    assert info.dataset_name == "DeepPCB"
    assert info.preparation_status == "prepared_and_validated"
    assert info.leakage_status == "verified_zero_leakage"
    assert info.total_images == 1500
    assert info.total_annotations > 9000
    assert len(info.splits) == 3
    assert len(info.class_distribution) == 6
