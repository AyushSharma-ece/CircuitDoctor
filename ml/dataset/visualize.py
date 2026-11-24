"""
CircuitDoctor - Visual Annotation Verification Tool
Renders YOLO bounding boxes, class labels, and severity indicators directly
onto actual PCB images to visually inspect conversion accuracy.
"""

from pathlib import Path
from typing import List, Optional
import cv2
import numpy as np

from backend.app.core.defect_classes import DEFECT_CLASSES, get_class_info

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TARGET_DATASET_DIR = BASE_DIR / "datasets" / "pcb_defects"
VIS_OUTPUT_DIR = BASE_DIR / "ml" / "dataset" / "visualizations"

def draw_yolo_annotations(
    image_path: Path,
    label_path: Path,
    output_path: Optional[Path] = None
) -> np.ndarray:
    """
    Overlay YOLO bounding boxes onto PCB image.
    Uses class-specific hex colors defined in core defect_classes.py.
    """
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    h, w = image.shape[:2]

    if label_path.exists():
        lines = label_path.read_text(encoding="utf-8").strip().splitlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            cid = int(parts[0])
            cx, cy, bw, bh = map(float, parts[1:])

            # Convert normalized center-size to absolute corners
            x1 = int(round((cx - bw / 2.0) * w))
            y1 = int(round((cy - bh / 2.0) * h))
            x2 = int(round((cx + bw / 2.0) * w))
            y2 = int(round((cy + bh / 2.0) * h))

            # Clamp
            x1 = max(0, min(w - 1, x1))
            y1 = max(0, min(h - 1, y1))
            x2 = max(0, min(w - 1, x2))
            y2 = max(0, min(h - 1, y2))

            class_info = get_class_info(cid)
            name = class_info["name"]
            # Color RGB to BGR for OpenCV
            r, g, b = class_info["color_rgb"]
            color_bgr = (b, g, r)

            # Draw bounding box rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), color_bgr, 2)

            # Label banner
            label_text = f"{name} (#{cid})"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.42
            font_thickness = 1
            text_size, _ = cv2.getTextSize(label_text, font, font_scale, font_thickness)
            
            # Label background box
            label_y1 = max(0, y1 - text_size[1] - 6)
            label_y2 = y1
            label_x2 = min(w, x1 + text_size[0] + 6)
            
            cv2.rectangle(image, (x1, label_y1), (label_x2, label_y2), color_bgr, -1)
            cv2.putText(
                image,
                label_text,
                (x1 + 3, label_y2 - 3),
                font,
                font_scale,
                (255, 255, 255),
                font_thickness,
                lineType=cv2.LINE_AA
            )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)

    return image

def generate_sample_visualizations(
    dataset_dir: Path = TARGET_DATASET_DIR,
    output_dir: Path = VIS_OUTPUT_DIR,
    samples_per_split: int = 3
) -> List[Path]:
    """Generate visual verification images for each split (train, val, test)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_paths = []

    for split in ["train", "val", "test"]:
        img_dir = dataset_dir / "images" / split
        lbl_dir = dataset_dir / "labels" / split

        if not img_dir.exists():
            continue

        images = sorted(list(img_dir.glob("*.jpg")))[:samples_per_split]
        for img_path in images:
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            out_path = output_dir / f"annotated_{split}_{img_path.stem}.jpg"
            draw_yolo_annotations(img_path, lbl_path, out_path)
            generated_paths.append(out_path)
            print(f"[Visual Verification] Generated {out_path.name}")

    return generated_paths

if __name__ == "__main__":
    paths = generate_sample_visualizations()
    print(f"Generated {len(paths)} verification images in {VIS_OUTPUT_DIR}")
