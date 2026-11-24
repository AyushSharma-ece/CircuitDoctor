"""
CircuitDoctor - End-to-End Dataset Engineering Orchestrator
Executes complete DeepPCB download, extraction, coordinate conversion,
leakage-safe partitioning, validation, and visual verification.
"""

import sys
import time
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.dataset.download import download_deeppcb, extract_deeppcb
from ml.dataset.split import build_yolo_dataset
from ml.dataset.validator import validate_yolo_dataset, print_validation_report
from ml.dataset.visualize import generate_sample_visualizations

def run_dataset_pipeline(force_download: bool = False, force_extract: bool = False):
    """Execute complete dataset engineering workflow."""
    start_time = time.time()
    print("\n" + "=" * 65)
    print("      CIRCUITDOCTOR: MILESTONE 2 - DATASET ENGINEERING")
    print("=" * 65)

    # 1. Download
    print("\n[Step 1/5] Checking / Downloading DeepPCB Dataset...")
    archive_path = download_deeppcb(force=force_download)

    # 2. Extract
    print("\n[Step 2/5] Extracting Raw PCB Data...")
    pcb_data_dir = extract_deeppcb(archive_path, force=force_extract)

    # 3. Convert & Partition
    print("\n[Step 3/5] Converting Annotations to YOLO Format & Partitioning...")
    split_stats = build_yolo_dataset(
        pcb_data_dir=pcb_data_dir,
        train_ratio=0.70,
        val_ratio=0.20,
        test_ratio=0.10
    )

    # 4. Validate Integrity & Leakage
    print("\n[Step 4/5] Executing Rigorous Dataset Integrity Validation...")
    validation_report = validate_yolo_dataset()
    print_validation_report(validation_report)

    if validation_report["status"] != "PASSED":
        print("[CRITICAL] Dataset validation failed. Please check errors listed above.")
        sys.exit(1)

    # 5. Visual Annotations Verification
    print("[Step 5/5] Generating Visual Ground-Truth Verification Samples...")
    vis_paths = generate_sample_visualizations(samples_per_split=3)

    elapsed = time.time() - start_time
    print(f"\n[DONE] Milestone 2 Dataset Pipeline completed successfully in {elapsed:.1f}s.")
    print(f"       YOLO Dataset:       datasets/pcb_defects/")
    print(f"       YOLO Config:        ml/configs/pcb_defects.yaml")
    print(f"       Visual Samples:     ml/dataset/visualizations/ ({len(vis_paths)} images)")
    print("=" * 65 + "\n")

    return validation_report

if __name__ == "__main__":
    run_dataset_pipeline()
