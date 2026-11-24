# CircuitDoctor - Model Training & Evaluation Guide

## 1. Overview

CircuitDoctor utilizes an object detection architecture based on Ultralytics YOLO (YOLO11n / YOLOv8n / YOLO26n) to identify and localize 6 visual defect categories on Printed Circuit Board surfaces from the DeepPCB dataset.

This guide provides technical specifications, training pipelines, hardware recommendations, and evaluation protocols.

---

## 2. Model Architecture & Hyperparameters

### Model Variants
- **Baseline Model:** `YOLO11n` (2.6M parameters) - Ultra-lightweight, high-speed inference suitable for real-time Automated Optical Inspection (AOI).
- **Alternative Variant:** `YOLOv8n` (3.2M parameters) - Industry-tested standard baseline.
- **Future Extension:** `YOLO26s` / `YOLO11s` (9.4M parameters) - Higher capacity for subtle low-contrast defects.

### Hyperparameter Configuration
- **Task:** Object Detection (`detect`)
- **Input Resolution:** $640 \times 640$ pixels
- **Batch Size:** 8 (or 16 for GPUs with $\ge 6$ GB VRAM)
- **Optimizer:** Auto (SGD with momentum 0.937 or AdamW)
- **Initial Learning Rate ($\text{lr}_0$):** 0.01
- **Weight Decay:** 0.0005
- **Augmentation Pipeline:** Mosaic (0.5), HSV hue/saturation perturbation, horizontal flip (no random affine rotation that breaks trace continuity semantics).

---

## 3. Dataset Configuration (`ml/configs/pcb_defects.yaml`)

```yaml
path: C:/Users/Ayush/OneDrive/Documents/CircuitDoctor/datasets/pcb_defects
train: images/train
val: images/val
test: images/test
nc: 6
names:
  0: 'Missing Hole'
  1: 'Mouse Bite'
  2: 'Open Circuit'
  3: 'Short'
  4: 'Spur'
  5: 'Spurious Copper'
```

### Partitioning Strategy (Leakage-Safe)
- **Train Split (71.2%):** 1,068 images | 7,171 bounding boxes
- **Validation Split (21.3%):** 320 images | 2,149 bounding boxes
- **Test Split (7.5%):** 112 images | 693 bounding boxes
- **Data Leakage Prevention:** Board design groups are partitioned contiguously so test pairs never share the identical master layout with training samples.

---

## 4. Training the Model

To execute model training:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" ml/training/train.py `
    --epochs 10 `
    --batch 8 `
    --imgsz 640 `
    --model models/yolo11n.pt `
    --device auto
```

### Outputs Generated:
- Checkpoints: `runs/detect/pcb_yolo_train/weights/best.pt` and `last.pt`
- Production Model: `models/best.pt`
- Training Metadata: `models/training_summary.json`

---

## 5. Evaluation Protocol (Untouched Test Split)

Evaluation is performed exclusively on the untouched test split (`datasets/pcb_defects/images/test`) to report unbiased real-world generalization:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" ml/evaluation/evaluate.py `
    --model models/best.pt `
    --data ml/configs/pcb_defects.yaml `
    --split test
```

### Metrics Recorded:
1. **Mean Average Precision (mAP):**
   - $\text{mAP}@0.5$: Metric at 50% Intersection over Union.
   - $\text{mAP}@0.5:0.95$: Stringent COCO-style metric across IoU thresholds from 0.50 to 0.95.
2. **Precision & Recall:** Overall and per defect class.
3. **Inference Latency:** Preprocess, neural forward pass, and NMS post-processing times in milliseconds.
4. **Visual Diagnostic Artifacts:**
   - Normalized Confusion Matrix: `models/eval_plots/confusion_matrix_normalized.png`
   - Precision-Recall Curve: `models/eval_plots/PR_curve.png`
   - F1-Score vs. Confidence Curve: `models/eval_plots/F1_curve.png`

---

## 6. Critical Technical Limitation: Optical vs. Electrical Boundary

> [!WARNING]
> Visual detection indicates the presence of a visual anomaly on the PCB surface. An optical visual inspection system cannot conclusively determine whether an apparent "short" is electrically conductive (under solder mask or passivation) or whether an apparent "open circuit" lacks an internal buried inner-layer connection. Always conduct electrical continuity, 4-wire resistance, and hi-pot isolation tests to verify functional failure.
