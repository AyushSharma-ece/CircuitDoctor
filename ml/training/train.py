"""
CircuitDoctor - Model Training Pipeline
Trains Ultralytics YOLO object detection models on the converted DeepPCB dataset.
Supports transfer learning, dynamic GPU/CPU detection, and hyperparameter configuration.
"""

import os
import sys
import json
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Set local YOLO config directory within the workspace to avoid AppData permissions
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.environ["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / ".ultralytics")

import torch
from ultralytics import YOLO

# Root directory of CircuitDoctor
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_YAML = PROJECT_ROOT / "ml" / "configs" / "pcb_defects.yaml"
MODELS_DIR = PROJECT_ROOT / "models"


def detect_optimal_device(requested_device: str = "auto") -> str:
    """Detect and return optimal hardware compute device."""
    if requested_device != "auto":
        return requested_device

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
        print(f"[Device] CUDA GPU detected: {gpu_name} ({gpu_mem:.0f} MiB VRAM)")
        return "0"
    else:
        print("[Device] No CUDA GPU available. Utilizing CPU.")
        return "cpu"


def train_pcb_detector(
    data_yaml: str = str(DEFAULT_DATA_YAML),
    base_model: str = "yolo11n.pt",
    epochs: int = 10,
    batch_size: int = 8,
    imgsz: int = 640,
    device: str = "auto",
    workers: int = 2,
    project: str = "runs/detect",
    name: str = "pcb_yolo_train",
    lr0: float = 0.01,
    patience: int = 20,
) -> dict:
    """Train YOLO model on PCB defect dataset and persist best weights."""
    target_device = detect_optimal_device(device)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 65)
    print(" CIRCUITDOCTOR - PCB DEFECT DETECTION TRAINING PIPELINE")
    print("=" * 65)
    print(f" Dataset Config : {data_yaml}")
    print(f" Base Weights   : {base_model}")
    print(f" Epochs         : {epochs}")
    print(f" Batch Size     : {batch_size}")
    print(f" Image Size     : {imgsz}x{imgsz}")
    print(f" Compute Device : {target_device}")
    print(f" Workers        : {workers}")
    print(f" Output Project : {project}/{name}")
    print("=" * 65 + "\n")

    start_time = time.time()
    start_iso = datetime.utcnow().isoformat()

    # Load baseline model for transfer learning
    model = YOLO(base_model)

    # Execute training
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=target_device,
        workers=workers,
        project=project,
        name=name,
        exist_ok=True,
        pretrained=True,
        plots=True,
        lr0=lr0,
        patience=patience,
        save=True,
        verbose=True,
    )

    training_duration_sec = round(time.time() - start_time, 2)
    print(f"\n[Training] Completed in {training_duration_sec:.1f} seconds.")

    # Locate saved weights
    run_dir = Path(project) / name
    best_weights_path = run_dir / "weights" / "best.pt"
    last_weights_path = run_dir / "weights" / "last.pt"

    dest_best_path = MODELS_DIR / "best.pt"
    dest_last_path = MODELS_DIR / "last.pt"

    if best_weights_path.exists():
        shutil.copy2(best_weights_path, dest_best_path)
        print(f"[Model] Saved best model to: {dest_best_path}")
    elif last_weights_path.exists():
        shutil.copy2(last_weights_path, dest_best_path)
        print(f"[Model] Saved last model to: {dest_best_path}")
    else:
        print("[Warning] Trained weights not found at expected location.")

    # Collect training summary
    summary = {
        "status": "completed",
        "timestamp_start": start_iso,
        "timestamp_end": datetime.utcnow().isoformat(),
        "duration_seconds": training_duration_sec,
        "base_model": base_model,
        "dataset_config": str(data_yaml),
        "hyperparameters": {
            "epochs": epochs,
            "batch_size": batch_size,
            "imgsz": imgsz,
            "device": target_device,
            "lr0": lr0,
            "patience": patience,
        },
        "weights": {
            "best_pt": str(dest_best_path.resolve()) if dest_best_path.exists() else None,
            "run_dir": str(run_dir.resolve()),
        },
    }

    summary_file = MODELS_DIR / "training_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"[Summary] Saved training summary to: {summary_file}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Train CircuitDoctor YOLO defect detection model.")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_YAML), help="Path to data YAML.")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Base model weights or architecture.")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs.")
    parser.add_argument("--batch", type=int, default=8, help="Batch size.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution.")
    parser.add_argument("--device", type=str, default="auto", help="Compute device ('0', 'cpu', 'auto').")
    parser.add_argument("--workers", type=int, default=2, help="DataLoader workers.")
    parser.add_argument("--project", type=str, default="runs/detect", help="Output project folder.")
    parser.add_argument("--name", type=str, default="pcb_yolo_train", help="Run experiment name.")

    args = parser.parse_args()

    train_pcb_detector(
        data_yaml=args.data,
        base_model=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
    )


if __name__ == "__main__":
    main()
