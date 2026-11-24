"""
CircuitDoctor - Detection Service
Singleton YOLO defect detection inference engine.
Loads model once on startup, runs inference on PCB images, generates color-coded annotated overlays,
and packages rich diagnostic metadata following the optical vs. electrical testing boundary.
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np

# Ensure workspace local config directory for Ultralytics
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
os.environ["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / ".ultralytics")

from backend.app.core.defect_classes import DEFECT_CLASSES, get_class_info, get_class_name

# Default model location
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"
FALLBACK_MODEL_PATH = PROJECT_ROOT / "models" / "yolo11n.pt"
ANNOTATED_DIR = PROJECT_ROOT / "backend" / "annotated"


class DetectionService:
    _instance: Optional["DetectionService"] = None
    _model = None
    _model_path: Optional[str] = None
    _device: str = "cpu"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "DetectionService":
        if cls._instance is None:
            cls._instance = DetectionService()
        return cls._instance

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load YOLO model once into memory if not already loaded."""
        if self._model is not None and (model_path is None or model_path == self._model_path):
            return True

        from ultralytics import YOLO
        import torch

        # Device determination
        self._device = "0" if torch.cuda.is_available() else "cpu"

        # Determine target model path
        target_path = None
        if model_path and Path(model_path).exists():
            target_path = Path(model_path)
        elif DEFAULT_MODEL_PATH.exists():
            target_path = DEFAULT_MODEL_PATH
        elif FALLBACK_MODEL_PATH.exists():
            target_path = FALLBACK_MODEL_PATH
        elif (PROJECT_ROOT / "yolo11n.pt").exists():
            target_path = PROJECT_ROOT / "yolo11n.pt"

        if target_path is None or not target_path.exists():
            print(f"[DetectionService] Warning: No trained weights found at {DEFAULT_MODEL_PATH}")
            return False

        try:
            print(f"[DetectionService] Loading YOLO model from {target_path} on device {self._device}...")
            self._model = YOLO(str(target_path))
            self._model_path = str(target_path)
            print("[DetectionService] Model loaded and ready for inference.")
            return True
        except Exception as e:
            print(f"[DetectionService] Error loading model: {e}")
            self._model = None
            return False

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    @property
    def model_path(self) -> Optional[str]:
        return self._model_path

    @property
    def device(self) -> str:
        return self._device

    def detect(
        self,
        image_path: str,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        save_annotated: bool = True
    ) -> Dict[str, Any]:
        """
        Run inference on PCB image, annotate defect regions, and return rich diagnostic report.
        """
        if not self.is_loaded:
            if not self.load_model():
                raise RuntimeError("Detection model is not loaded and no valid weights are available.")

        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Input image not found: {image_path}")

        # Read image to obtain original dimensions
        orig_img = cv2.imread(str(image_path_obj))
        if orig_img is None:
            raise ValueError(f"Could not decode image at: {image_path}")

        height, width = orig_img.shape[:2]

        # Execute neural inference with latency measurement
        start_time = time.time()
        results = self._model.predict(
            source=str(image_path_obj),
            conf=conf_threshold,
            iou=iou_threshold,
            imgsz=640,
            device=self._device,
            verbose=False,
        )
        inference_time_ms = round((time.time() - start_time) * 1000, 2)

        # Parse detection outputs
        detections: List[Dict[str, Any]] = []
        category_counts: Dict[str, int] = {}
        severity_counts = {"critical": 0, "medium": 0, "low": 0}

        annotated_img = orig_img.copy()

        if results and len(results) > 0:
            boxes = results[0].boxes
            for idx, box in enumerate(boxes):
                coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])

                x1, y1, x2, y2 = [int(round(c)) for c in coords]
                # Clamp coordinates to image bounds
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width - 1, x2), min(height - 1, y2)

                class_info = get_class_info(cls_id)
                class_name = class_info["name"]
                severity = class_info.get("severity", "medium")
                electrical_risk = class_info.get("electrical_risk", "Unspecified.")
                verification_advice = class_info.get("verification_advice", "Electrical testing required.")

                category_counts[class_name] = category_counts.get(class_name, 0) + 1
                if severity in severity_counts:
                    severity_counts[severity] += 1

                det_record = {
                    "detection_id": idx + 1,
                    "class_id": cls_id,
                    "class_name": class_name,
                    "confidence": round(conf, 4),
                    "confidence_pct": round(conf * 100, 1),
                    "bbox": [x1, y1, x2, y2],
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "severity": severity,
                    "electrical_risk": electrical_risk,
                    "verification_advice": verification_advice,
                    "color_hex": class_info.get("color_hex", "#ef4444"),
                }
                detections.append(det_record)

                # Draw annotation on image
                rgb = class_info.get("color_rgb", (239, 68, 68))
                bgr = (rgb[2], rgb[1], rgb[0])  # OpenCV uses BGR

                # High-contrast bounding box
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), bgr, 2)

                # Corner accent brackets for precision industrial look
                bracket_len = min(15, (x2 - x1) // 3, (y2 - y1) // 3)
                if bracket_len > 3:
                    cv2.line(annotated_img, (x1, y1), (x1 + bracket_len, y1), (255, 255, 255), 2)
                    cv2.line(annotated_img, (x1, y1), (x1, y1 + bracket_len), (255, 255, 255), 2)
                    cv2.line(annotated_img, (x2, y2), (x2 - bracket_len, y2), (255, 255, 255), 2)
                    cv2.line(annotated_img, (x2, y2), (x2, y2 - bracket_len), (255, 255, 255), 2)

                # Text label banner
                label_text = f"{class_name} {conf * 100:.1f}%"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.45
                thickness = 1
                (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)

                banner_y1 = max(0, y1 - text_h - 6)
                banner_y2 = y1
                banner_x2 = min(width, x1 + text_w + 8)

                # Background filled rectangle for text readability
                cv2.rectangle(annotated_img, (x1, banner_y1), (banner_x2, banner_y2), bgr, -1)
                # Text in crisp white
                cv2.putText(
                    annotated_img,
                    label_text,
                    (x1 + 4, banner_y2 - 3),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness,
                    cv2.LINE_AA,
                )

        # Save annotated image
        annotated_filename = f"annotated_{image_path_obj.stem}_{int(time.time())}.jpg"
        annotated_path = ANNOTATED_DIR / annotated_filename

        if save_annotated:
            cv2.imwrite(str(annotated_path), annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 92])

        total_defects = len(detections)
        if total_defects == 0:
            visual_status = "pass"
        elif severity_counts["critical"] > 0:
            visual_status = "fail"
        else:
            visual_status = "warning"

        return {
            "total_defects": total_defects,
            "visual_status": visual_status,
            "inference_time_ms": inference_time_ms,
            "image_width": width,
            "image_height": height,
            "detections": detections,
            "category_counts": category_counts,
            "severity_breakdown": severity_counts,
            "annotated_image_path": str(annotated_path) if save_annotated else None,
            "annotated_filename": annotated_filename if save_annotated else None,
            "optical_disclaimer": (
                "Optical visual inspection results are visual defect predictions only. "
                "Non-destructive visual inspection cannot conclusively confirm electrical short circuits, "
                "open connections, component tolerances, or functional continuity. "
                "Physical electrical testing (DMM continuity, 4-wire Kelvin resistance, hi-pot isolation) is recommended."
            ),
        }
