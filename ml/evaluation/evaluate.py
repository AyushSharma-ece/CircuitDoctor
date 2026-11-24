"""
CircuitDoctor - Model Evaluation Pipeline
Evaluates trained YOLO PCB defect detection models on the untouched test split.
Computes real Precision, Recall, mAP@50, mAP@50-95, per-class metrics, and inference latency.
"""

import os
import sys
import json
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Set local YOLO config directory within the workspace
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.environ["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / ".ultralytics")

import torch
from ultralytics import YOLO

# Root directory of CircuitDoctor
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_YAML = PROJECT_ROOT / "ml" / "configs" / "pcb_defects.yaml"
MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "best.pt"

# Canonical defect class mapping
CLASS_MAPPING = {
    0: "Missing Hole",
    1: "Mouse Bite",
    2: "Open Circuit",
    3: "Short",
    4: "Spur",
    5: "Spurious Copper",
}


def detect_optimal_device(requested_device: str = "auto") -> str:
    """Detect and return optimal hardware compute device."""
    if requested_device != "auto":
        return requested_device

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"[Device] Evaluating on CUDA GPU: {gpu_name}")
        return "0"
    else:
        print("[Device] Evaluating on CPU.")
        return "cpu"


def evaluate_pcb_detector(
    model_path: str = str(DEFAULT_MODEL_PATH),
    data_yaml: str = str(DEFAULT_DATA_YAML),
    split: str = "test",
    batch_size: int = 8,
    imgsz: int = 640,
    device: str = "auto",
    project: str = "runs/detect",
    name: str = "pcb_yolo_eval",
) -> dict:
    """Evaluate YOLO model on the test partition and persist rigorous metrics."""
    target_device = detect_optimal_device(device)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    eval_plots_dir = MODELS_DIR / "eval_plots"
    eval_plots_dir.mkdir(parents=True, exist_ok=True)

    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    print("\n" + "=" * 65)
    print(" CIRCUITDOCTOR - PCB DEFECT DETECTION EVALUATION PIPELINE")
    print("=" * 65)
    print(f" Model Weights   : {model_path}")
    print(f" Dataset Config  : {data_yaml}")
    print(f" Evaluation Split: {split} (Untouched Test Partition)")
    print(f" Image Size      : {imgsz}x{imgsz}")
    print(f" Batch Size      : {batch_size}")
    print(f" Device          : {target_device}")
    print("=" * 65 + "\n")

    start_time = time.time()
    model = YOLO(str(model_file))

    # Run validation on the specified split (strictly 'test' for final benchmark)
    metrics = model.val(
        data=str(data_yaml),
        split=split,
        batch=batch_size,
        imgsz=imgsz,
        device=target_device,
        project=project,
        name=name,
        exist_ok=True,
        plots=True,
        verbose=True,
    )

    eval_duration_sec = round(time.time() - start_time, 2)

    # Extract high-level metrics
    map50 = float(metrics.box.map50)
    map75 = float(metrics.box.map75) if hasattr(metrics.box, "map75") else 0.0
    map50_95 = float(metrics.box.map)
    mean_precision = float(metrics.box.mp)
    mean_recall = float(metrics.box.mr)

    # Extract class-level metrics
    per_class_metrics = {}
    class_names = metrics.names if hasattr(metrics, "names") else CLASS_MAPPING

    # Extract per-class arrays if available
    ap50_list = metrics.box.ap50.tolist() if hasattr(metrics.box, "ap50") and hasattr(metrics.box.ap50, "tolist") else []
    ap_list = metrics.box.maps.tolist() if hasattr(metrics.box, "maps") and hasattr(metrics.box.maps, "tolist") else []
    p_list = metrics.box.p.tolist() if hasattr(metrics.box, "p") and hasattr(metrics.box.p, "tolist") else []
    r_list = metrics.box.r.tolist() if hasattr(metrics.box, "r") and hasattr(metrics.box.r, "tolist") else []

    for idx, name_key in enumerate(class_names.values() if isinstance(class_names, dict) else class_names):
        c_id = idx
        c_name = CLASS_MAPPING.get(c_id, str(name_key))
        c_map50 = float(ap50_list[idx]) if idx < len(ap50_list) else 0.0
        c_map50_95 = float(ap_list[idx]) if idx < len(ap_list) else 0.0
        c_precision = float(p_list[idx]) if idx < len(p_list) else 0.0
        c_recall = float(r_list[idx]) if idx < len(r_list) else 0.0

        per_class_metrics[str(c_id)] = {
            "class_id": c_id,
            "class_name": c_name,
            "map50": round(c_map50, 4),
            "map50_95": round(c_map50_95, 4),
            "precision": round(c_precision, 4),
            "recall": round(c_recall, 4),
        }

    # Extract speed metrics
    speed = {
        "preprocess_ms": round(float(metrics.speed.get("preprocess", 0.0)), 2),
        "inference_ms": round(float(metrics.speed.get("inference", 0.0)), 2),
        "loss_ms": round(float(metrics.speed.get("loss", 0.0)), 2),
        "postprocess_ms": round(float(metrics.speed.get("postprocess", 0.0)), 2),
    }
    speed["total_ms"] = round(sum(speed.values()), 2)

    # Copy generated evaluation plots
    run_dir = Path(project) / name
    copied_plots = []
    plot_names = [
        "confusion_matrix.png",
        "confusion_matrix_normalized.png",
        "PR_curve.png",
        "F1_curve.png",
        "P_curve.png",
        "R_curve.png",
        "val_batch0_labels.jpg",
        "val_batch0_pred.jpg",
    ]

    for p_name in plot_names:
        src = run_dir / p_name
        if src.exists():
            dst = eval_plots_dir / p_name
            shutil.copy2(src, dst)
            copied_plots.append(p_name)

    # Compile structured metrics artifact
    evaluation_record = {
        "evaluation_timestamp": datetime.utcnow().isoformat(),
        "model_file": str(model_file.resolve()),
        "evaluation_split": split,
        "dataset_yaml": str(data_yaml),
        "summary": {
            "mAP50": round(map50, 4),
            "mAP75": round(map75, 4),
            "mAP50_95": round(map50_95, 4),
            "mean_precision": round(mean_precision, 4),
            "mean_recall": round(mean_recall, 4),
        },
        "per_class": per_class_metrics,
        "speed": speed,
        "hardware": {
            "device": target_device,
            "duration_seconds": eval_duration_sec,
        },
        "plots_saved": copied_plots,
    }

    output_json = MODELS_DIR / "evaluation_metrics.json"
    with open(output_json, "w") as f:
        json.dump(evaluation_record, f, indent=2)

    print(f"\n[Evaluation] Successfully saved metrics to: {output_json}")
    print("\n--- Summary Performance on Untouched Test Split ---")
    print(f" Precision : {mean_precision * 100:.2f}%")
    print(f" Recall    : {mean_recall * 100:.2f}%")
    print(f" mAP@50    : {map50 * 100:.2f}%")
    print(f" mAP@50-95 : {map50_95 * 100:.2f}%")
    print(f" Latency   : {speed['inference_ms']} ms/image")
    print("--------------------------------------------------\n")

    return evaluation_record


def main():
    parser = argparse.ArgumentParser(description="Evaluate CircuitDoctor YOLO defect detection model.")
    parser.add_argument("--model", type=str, default=str(DEFAULT_MODEL_PATH), help="Path to model .pt file.")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_YAML), help="Path to data YAML.")
    parser.add_argument("--split", type=str, default="test", help="Evaluation split ('test' or 'val').")
    parser.add_argument("--batch", type=int, default=8, help="Batch size.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution.")
    parser.add_argument("--device", type=str, default="auto", help="Compute device ('0', 'cpu', 'auto').")
    parser.add_argument("--project", type=str, default="runs/detect", help="Output project folder.")
    parser.add_argument("--name", type=str, default="pcb_yolo_eval", help="Evaluation run name.")

    args = parser.parse_args()

    evaluate_pcb_detector(
        model_path=args.model,
        data_yaml=args.data,
        split=args.split,
        batch_size=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()
