"""
CircuitDoctor - Leakage-Safe Dataset Splitter & YOLO Dataset Generator
Organizes DeepPCB images into training (70%), validation (20%), and testing (10%)
subsets while guaranteeing zero data leakage between PCB board designs.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any

from ml.dataset.converter import parse_deeppcb_annotation_file, format_yolo_lines
from backend.app.core.defect_classes import DEFECT_CLASSES

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
TARGET_DATASET_DIR = DATASETS_DIR / "pcb_defects"
CONFIGS_DIR = BASE_DIR / "ml" / "configs"

def discover_deeppcb_samples(pcb_data_dir: Path) -> List[Dict[str, Any]]:
    """
    Traverse PCBData directory structure and discover all valid
    (test_image, template_image, annotation_file) sample tuples.
    """
    samples = []
    
    # Iterate through all group directories
    group_dirs = sorted([d for d in pcb_data_dir.iterdir() if d.is_dir() and d.name.startswith("group")])
    
    for g_dir in group_dirs:
        group_id = g_dir.name
        # Subdirectories inside group: e.g. group00041/00041 and group00041/00041_not
        img_subdirs = [d for d in g_dir.iterdir() if d.is_dir() and not d.name.endswith("_not")]
        annot_subdirs = [d for d in g_dir.iterdir() if d.is_dir() and d.name.endswith("_not")]
        
        if not img_subdirs or not annot_subdirs:
            continue
            
        img_dir = img_subdirs[0]
        annot_dir = annot_subdirs[0]
        
        # Test images end with _test.jpg
        test_images = sorted(list(img_dir.glob("*_test.jpg")))
        
        for test_img in test_images:
            sample_id = test_img.stem.replace("_test", "")
            temp_img = img_dir / f"{sample_id}_temp.jpg"
            annot_file = annot_dir / f"{sample_id}.txt"
            
            if annot_file.exists():
                samples.append({
                    "id": sample_id,
                    "group": group_id,
                    "test_image": test_img,
                    "temp_image": temp_img if temp_img.exists() else None,
                    "annotation_file": annot_file,
                })
                
    return samples

def partition_samples_leakage_safe(
    samples: List[Dict[str, Any]],
    train_ratio: float = 0.70,
    val_ratio: float = 0.20,
    test_ratio: float = 0.10
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Partition samples into train, val, and test subsets grouped by PCB board groups
    to ensure that related board templates and geometries never cross partition boundaries.
    """
    # Group samples by group_id
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for s in samples:
        gid = s["group"]
        if gid not in groups:
            groups[gid] = []
        groups[gid].append(s)
        
    total_samples = len(samples)
    target_train_count = int(total_samples * train_ratio)
    target_val_count = int(total_samples * val_ratio)
    target_test_count = total_samples - target_train_count - target_val_count
    
    # Sort groups deterministically by sample count descending for balanced bin-packing
    sorted_group_names = sorted(groups.keys(), key=lambda g: len(groups[g]), reverse=True)
    
    splits: Dict[str, List[Dict[str, Any]]] = {
        "train": [],
        "val": [],
        "test": []
    }
    
    # Bin-packing assignment by entire board groups
    train_count = 0
    val_count = 0
    test_count = 0
    
    for gname in sorted_group_names:
        g_samples = groups[gname]
        g_len = len(g_samples)
        
        # Assign to the split furthest below its target
        train_deficit = target_train_count - train_count
        val_deficit = target_val_count - val_count
        test_deficit = target_test_count - test_count
        
        if train_deficit >= val_deficit and train_deficit >= test_deficit:
            splits["train"].extend(g_samples)
            train_count += g_len
        elif val_deficit >= test_deficit:
            splits["val"].extend(g_samples)
            val_count += g_len
        else:
            splits["test"].extend(g_samples)
            test_count += g_len
            
    return splits

def build_yolo_dataset(
    pcb_data_dir: Path,
    output_dir: Path = TARGET_DATASET_DIR,
    train_ratio: float = 0.70,
    val_ratio: float = 0.20,
    test_ratio: float = 0.10,
    include_template_negatives: bool = False
) -> Dict[str, Any]:
    """
    Convert DeepPCB annotations to YOLO format, partition leakage-safely,
    and generate standard YOLO directory layout and data.yaml configuration.
    """
    samples = discover_deeppcb_samples(pcb_data_dir)
    if not samples:
        raise ValueError(f"No valid DeepPCB samples found in {pcb_data_dir}")
        
    print(f"[Dataset Split] Discovered {len(samples)} annotated test PCB samples across groups.")
    
    splits = partition_samples_leakage_safe(
        samples,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio
    )
    
    print(f"[Dataset Split] Partition Allocation:")
    print(f"  - Train: {len(splits['train'])} samples ({len(splits['train'])/len(samples)*100:.1f}%)")
    print(f"  - Val:   {len(splits['val'])} samples ({len(splits['val'])/len(samples)*100:.1f}%)")
    print(f"  - Test:  {len(splits['test'])} samples ({len(splits['test'])/len(samples)*100:.1f}%)")
    
    # Initialize YOLO directory structure
    for split_name in ["train", "val", "test"]:
        (output_dir / "images" / split_name).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split_name).mkdir(parents=True, exist_ok=True)
        
    stats_summary = {
        "total_samples": len(samples),
        "splits": {},
        "class_counts": {cid: 0 for cid in sorted(DEFECT_CLASSES.keys())}
    }
    
    # Process each partition
    for split_name, split_samples in splits.items():
        split_img_dir = output_dir / "images" / split_name
        split_lbl_dir = output_dir / "labels" / split_name
        
        split_class_counts = {cid: 0 for cid in sorted(DEFECT_CLASSES.keys())}
        split_defect_instances = 0
        
        for sample in split_samples:
            sample_id = sample["id"]
            src_img = sample["test_image"]
            src_annot = sample["annotation_file"]
            
            # Destination file paths
            dest_img = split_img_dir / f"{sample_id}.jpg"
            dest_lbl = split_lbl_dir / f"{sample_id}.txt"
            
            # Copy test image
            shutil.copy2(src_img, dest_img)
            
            # Parse and convert annotations
            yolo_boxes = parse_deeppcb_annotation_file(str(src_annot), img_w=640, img_h=640)
            
            for cid, cx, cy, w, h in yolo_boxes:
                stats_summary["class_counts"][cid] += 1
                split_class_counts[cid] += 1
                split_defect_instances += 1
                
            # Write standard YOLO annotation file
            yolo_content = format_yolo_lines(yolo_boxes)
            with open(dest_lbl, "w", encoding="utf-8") as f:
                f.write(yolo_content)
                
        stats_summary["splits"][split_name] = {
            "image_count": len(split_samples),
            "defect_instances": split_defect_instances,
            "class_counts": split_class_counts,
            "groups": sorted(list(set(s["group"] for s in split_samples)))
        }
        
    # Generate YOLO dataset configuration yaml
    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    yaml_config_path = CONFIGS_DIR / "pcb_defects.yaml"
    
    clean_path = str(output_dir.resolve()).replace("\\", "/")
    
    yaml_lines = [
        f"path: {clean_path}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        f"nc: {len(DEFECT_CLASSES)}",
        "names:"
    ]
    for cid in sorted(DEFECT_CLASSES.keys()):
        yaml_lines.append(f"  {cid}: '{DEFECT_CLASSES[cid]['name']}'")
        
    yaml_content = "\n".join(yaml_lines) + "\n"
    
    with open(yaml_config_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)
        
    print(f"[Dataset Split] Generated YOLO configuration at: {yaml_config_path}")
    return stats_summary

if __name__ == "__main__":
    from ml.dataset.download import RAW_EXTRACT_DIR
    pcb_data = RAW_EXTRACT_DIR / "DeepPCB-master" / "PCBData"
    if pcb_data.exists():
        build_yolo_dataset(pcb_data)
    else:
        print(f"PCBData directory not found at {pcb_data}. Run download.py first.")
