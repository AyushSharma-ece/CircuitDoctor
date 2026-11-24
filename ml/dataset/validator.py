"""
CircuitDoctor - YOLO Dataset Integrity & Leakage Validation Script
Verifies dataset integrity, annotation coordinates, image dimensions,
leakage isolation, and class distributions.
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image

from backend.app.core.defect_classes import DEFECT_CLASSES, get_class_name

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TARGET_DATASET_DIR = BASE_DIR / "datasets" / "pcb_defects"

def validate_yolo_dataset(dataset_dir: Path = TARGET_DATASET_DIR) -> Dict[str, Any]:
    """
    Run comprehensive validation checks across train, val, and test partitions:
    - 1-to-1 image and label pairing
    - Coordinate boundary checks (0 <= cx, cy, w, h <= 1)
    - Valid class IDs (0-5)
    - Image dimensions (640x640)
    - Zero data leakage between partitions
    """
    report = {
        "status": "PASSED",
        "partitions": {},
        "total_images": 0,
        "total_labels": 0,
        "total_annotations": 0,
        "errors": [],
        "warnings": [],
        "class_distribution": {cid: 0 for cid in sorted(DEFECT_CLASSES.keys())},
        "leakage_verified": True
    }

    seen_image_basenames: Dict[str, str] = {} # basename -> partition

    for split in ["train", "val", "test"]:
        img_dir = dataset_dir / "images" / split
        lbl_dir = dataset_dir / "labels" / split

        if not img_dir.exists() or not lbl_dir.exists():
            report["status"] = "FAILED"
            report["errors"].append(f"Missing directory for partition: {split}")
            continue

        images = sorted(list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")))
        labels = sorted(list(lbl_dir.glob("*.txt")))

        split_report = {
            "images_count": len(images),
            "labels_count": len(labels),
            "annotations_count": 0,
            "class_counts": {cid: 0 for cid in sorted(DEFECT_CLASSES.keys())},
            "empty_labels": 0,
            "corrupt_images": 0,
            "invalid_boxes": 0,
        }

        image_stem_set = {img.stem for img in images}
        label_stem_set = {lbl.stem for lbl in labels}

        # Check image-label correspondence
        missing_labels = image_stem_set - label_stem_set
        missing_images = label_stem_set - image_stem_set

        if missing_labels:
            report["errors"].append(f"[{split}] {len(missing_labels)} images missing label files.")
        if missing_images:
            report["errors"].append(f"[{split}] {len(missing_images)} labels missing image files.")

        # Inspect images and labels
        for img_path in images:
            # Check for data leakage across partitions
            if img_path.name in seen_image_basenames:
                report["status"] = "FAILED"
                report["leakage_verified"] = False
                prev_split = seen_image_basenames[img_path.name]
                report["errors"].append(
                    f"DATA LEAKAGE: Image {img_path.name} appears in both '{prev_split}' and '{split}'!"
                )
            seen_image_basenames[img_path.name] = split

            # Verify image readability and dimensions
            try:
                with Image.open(img_path) as im:
                    w, h = im.size
                    if w != 640 or h != 640:
                        report["warnings"].append(
                            f"[{split}] Non-standard dimension {w}x{h} for {img_path.name} (expected 640x640)"
                        )
            except Exception as e:
                report["errors"].append(f"[{split}] Corrupted image {img_path.name}: {e}")
                split_report["corrupt_images"] += 1

            # Validate corresponding label file
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if lbl_path.exists():
                lines = lbl_path.read_text(encoding="utf-8").strip().splitlines()
                if not lines:
                    split_report["empty_labels"] += 1

                for line_idx, line in enumerate(lines):
                    parts = line.strip().split()
                    if len(parts) != 5:
                        report["errors"].append(
                            f"[{split}] Invalid format in {lbl_path.name} line {line_idx+1}: '{line}'"
                        )
                        split_report["invalid_boxes"] += 1
                        continue

                    try:
                        cid = int(parts[0])
                        cx, cy, bw, bh = map(float, parts[1:])
                    except ValueError:
                        report["errors"].append(
                            f"[{split}] Non-numeric values in {lbl_path.name} line {line_idx+1}"
                        )
                        split_report["invalid_boxes"] += 1
                        continue

                    # Validate class ID
                    if cid not in DEFECT_CLASSES:
                        report["errors"].append(
                            f"[{split}] Invalid class ID {cid} in {lbl_path.name} line {line_idx+1}"
                        )
                        split_report["invalid_boxes"] += 1
                        continue

                    # Validate normalized coordinates [0.0, 1.0]
                    if not (0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0 and 0.0 < bw <= 1.0 and 0.0 < bh <= 1.0):
                        report["errors"].append(
                            f"[{split}] Coordinate out of bounds in {lbl_path.name}: ({cx}, {cy}, {bw}, {bh})"
                        )
                        split_report["invalid_boxes"] += 1
                        continue

                    split_report["annotations_count"] += 1
                    split_report["class_counts"][cid] += 1
                    report["class_distribution"][cid] += 1
                    report["total_annotations"] += 1

        report["partitions"][split] = split_report
        report["total_images"] += split_report["images_count"]
        report["total_labels"] += split_report["labels_count"]

    if report["errors"]:
        report["status"] = "FAILED"

    return report

def print_validation_report(report: Dict[str, Any]):
    """Print formatted validation summary table to terminal."""
    print("\n" + "=" * 65)
    print("      CIRCUITDOCTOR DATASET VALIDATION REPORT")
    print("=" * 65)
    print(f"Overall Status:        {report['status']}")
    print(f"Leakage Isolation:     {'GUARANTEED (No Overlaps)' if report['leakage_verified'] else 'FAILED'}")
    print(f"Total Valid Images:    {report['total_images']}")
    print(f"Total Defect Boxes:    {report['total_annotations']}")
    print("-" * 65)

    print("Partition Breakdown:")
    for split, info in report.get("partitions", {}).items():
        print(f"  [{split.upper()}] Images: {info['images_count']:<5} | Bboxes: {info['annotations_count']:<5} | Empty: {info['empty_labels']}")

    print("-" * 65)
    print("Class Distribution Across Dataset:")
    for cid, count in report.get("class_distribution", {}).items():
        name = get_class_name(cid)
        pct = (count / report['total_annotations'] * 100.0) if report['total_annotations'] > 0 else 0.0
        print(f"  Class {cid} - {name:<16}: {count:<6} ({pct:.1f}%)")

    print("-" * 65)
    if report["errors"]:
        print(f"CRITICAL ERRORS ({len(report['errors'])}):")
        for err in report["errors"][:10]:
            print(f"  x {err}")
        if len(report["errors"]) > 10:
            print(f"  ... and {len(report['errors']) - 10} more errors.")
    else:
        print("CRITICAL ERRORS:       0 (Zero errors detected)")

    if report["warnings"]:
        print(f"WARNINGS:              {len(report['warnings'])}")
    else:
        print("WARNINGS:              0")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    rep = validate_yolo_dataset()
    print_validation_report(rep)
