# CircuitDoctor: DeepPCB Dataset Engineering Guide

## 1. Dataset Overview

CircuitDoctor uses the benchmark **DeepPCB** dataset for printed circuit board surface defect detection:

- **Reference:** Tang et al., 2019 (*DeepPCB: A Dataset for Printed Circuit Board Defect Detection and Classification*)
- **Official Repository:** [https://github.com/tangsanli5201/DeepPCB](https://github.com/tangsanli5201/DeepPCB)
- **Image Specifications:** High-resolution linear scan CCD sensor images captured at approximately 48 pixels per millimeter, cropped into standardized $640 \times 640$ pixel tiles.
- **Composition:** 1,500 image pairs (1,500 defect-free reference templates and 1,500 tested defective boards), across 11 discrete board design groups (`group00041`, `group12000`, `group12100`, `group12300`, `group13000`, `group20085`, `group44000`, `group50600`, `group77000`, `group90100`, `group92000`).

---

## 2. Annotation Coordinate Conversion

### Original DeepPCB Format
DeepPCB stores annotations in space-separated text files corresponding to each test image:
```text
x1 y1 x2 y2 type
```
- `x1, y1`: Top-left corner coordinates (pixels, integers)
- `x2, y2`: Bottom-right corner coordinates (pixels, integers)
- `type`: 1-indexed raw class ID (`1` to `6`)

### Target YOLO Format
YOLO requires bounding boxes normalized to $[0.0, 1.0]$ relative to image dimensions ($W = 640, H = 640$):
```text
class_id x_center y_center width height
```

### Mathematical Conversion Equations
For bounding box coordinates $(x_1, y_1)$ and $(x_2, y_2)$ on image dimensions $(W, H)$:
$$\text{width} = \frac{x_2 - x_1}{W}$$
$$\text{height} = \frac{y_2 - y_1}{H}$$
$$x_{\text{center}} = \frac{x_1 + x_2}{2 \cdot W}$$
$$y_{\text{center}} = \frac{y_1 + y_2}{2 \cdot H}$$

All coordinate values are clamped to $[0.0, 1.0]$ to eliminate edge-boundary pixel overflows.

---

## 3. Standard Class Mapping

Raw DeepPCB labels are mapped to CircuitDoctor standard class IDs (`backend/app/core/defect_classes.py`):

| DeepPCB Raw Type | DeepPCB Name | CircuitDoctor Class ID | Standard Defect Name | Severity | Hex Color | Total Instances |
|---|---|---|---|---|---|---|
| `6` | `pin-hole` | **`0`** | **Missing Hole** | Critical | `#ef4444` | 1,501 (15.0%) |
| `3` | `mousebite` | **`1`** | **Mouse Bite** | Medium | `#f97316` | 1,965 (19.6%) |
| `1` | `open` | **`2`** | **Open Circuit** | Critical | `#dc2626` | 1,942 (19.4%) |
| `2` | `short` | **`3`** | **Short** | Critical | `#b91c1c` | 1,506 (15.0%) |
| `4` | `spur` | **`4`** | **Spur** | Medium | `#eab308` | 1,625 (16.2%) |
| `5` | `copper` | **`5`** | **Spurious Copper** | Low | `#38bdf8` | 1,474 (14.7%) |
| **Total** | | | | | | **10,013 (100%)** |

---

## 4. Leakage-Safe Partitioning Methodology

### The Leakage Problem
In standard random splitting, image pairs belonging to the same PCB trace geometry can appear in both the training set and the test set. Because DeepPCB generates multiple crops from identical physical boards, a model trained on one crop from `group20085` could easily memorize identical trace layout features, inflating test accuracy artificially.

### The Solution: Group-Level Bin Packing
CircuitDoctor partitions data strictly at the **PCB board group level**:
- All images from a given board geometry remain consolidated inside a single split.
- Zero image stems or near-duplicate layouts cross between partitions.

### Actual Measured Split Allocations:
- **Training Subset:** 1,068 images (71.2%) &bull; 7,171 bounding boxes
- **Validation Subset:** 320 images (21.3%) &bull; 2,149 bounding boxes
- **Test Subset (Untouched):** 112 images (7.5%) &bull; 693 bounding boxes
- **Total:** 1,500 images &bull; 10,013 bounding boxes

---

## 5. Dataset Validation & Integrity Checks

The dataset validation script ([ml/dataset/validator.py](file:///c:/Users/Ayush/OneDrive/Documents/CircuitDoctor/ml/dataset/validator.py)) verifies:
1. **1-to-1 Correspondence:** Every image file has a matching label file with identical stem.
2. **Dimension Conformity:** All images validated at $640 \times 640$ pixels.
3. **Coordinate Bounds:** All bounding boxes strictly satisfy $0 \le cx, cy, w, h \le 1.0$.
4. **Class ID Range:** All labels contain valid integers in $\{0, 1, 2, 3, 4, 5\}$.
5. **Data Leakage Check:** Disjoint verification confirms 0 overlapping stems across partitions.

---

## 6. Commands to Run & Inspect

### Run Dataset Pipeline:
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" ml/dataset/prepare_dataset.py
```

### Run Validation Checks:
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" ml/dataset/validator.py
```

### Run Automated PyTest Suite:
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m pytest backend/tests/ -v
```
