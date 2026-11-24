# CircuitDoctor: Architectural Specification

## 1. System Philosophy & Domain Boundary

**CircuitDoctor** is an industrial automated optical inspection (AOI) software suite designed to identify, localize, and classify visible surface anomalies on Printed Circuit Boards (PCBs) using deep learning (YOLO).

### The Optical vs. Electrical Boundary Principle
In electronics manufacturing and testing:
- **Visual Inspection (CircuitDoctor)** identifies surface copper breaks, bridges, drill anomalies, and etching residues using high-resolution images.
- **Electrical Testing (Flying Probe / In-Circuit Testing)** measures electrical impedance, DC continuity, and dielectric isolation.
- Optical surface observation **cannot confirm** internal layer continuity, high-resistance necking under solder mask, or silicon component functional integrity.
- Consequently, all outputs are designated as **visual predictions**, and every classified defect is linked to specific electrical verification recommendations (e.g., Kelvin 4-wire resistance, hi-pot isolation, or DMM continuity testing).

---

## 2. Component Architecture

```
                    ┌────────────────────────────┐
                    │      Industrial User       │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      React 18 + Vite Frontend                          │
│  - Dark Navy Industrial Theme (#070b14 / #0f172a)                      │
│  - 8 Sidebar Navigation Views (Dashboard, Inspect, History, Model, etc)│
│  - Recharts Visual Analytics (Defect Distribution, Latency Tracking)   │
│  - Interactive Image Toggle (Original vs. Annotated PCB)               │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ HTTP / JSON / Multipart
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend Router                          │
│  - CORS Middleware (Localhost 5173 / 3000)                             │
│  - Strict Upload Validation (Magic bytes, max 25MB, dimensions)        │
│  - RESTful Endpoints:                                                  │
│      GET  /api/health            GET  /api/model/info                  │
│      POST /api/inspect           GET  /api/statistics                  │
│      GET  /api/inspections       DELETE /api/inspections/{id}          │
│      GET  /api/images/original   GET  /api/images/annotated            │
│      GET  /api/inspections/{id}/report                                 │
└───────────────┬─────────────────┬───────────────────┬──────────────────┘
                │                 │                   │
                ▼                 ▼                   ▼
┌───────────────────────┐ ┌───────────────┐ ┌────────────────────────────┐
│ SQLite Database       │ │ Storage Disk  │ │ YOLO Inference Service     │
│ - inspections table   │ │ - uploads/    │ │ - Ultralytics YOLO26n      │
│ - detections table    │ │ - annotated/  │ │ - Single startup load      │
│ - cascade deletion    │ │ - reports/    │ │ - Configurable conf & IoU  │
│ - SQLAlchemy models   │ │               │ │ - Bounding box annotation  │
└───────────────────────┘ └───────────────┘ └────────────────────────────┘
```

---

## 3. Standard Defect Classification Mapping

Defined in a single source of truth at `backend/app/core/defect_classes.py`:

| Class ID | Defect Category | Hex Color | Severity | Primary Electrical Risk | Required Electrical Test |
|---|---|---|---|---|---|
| `0` | Missing Hole | `#ef4444` | Critical | Via/through-hole open; missing THT pin | Coordinate probe + continuity check |
| `1` | Mouse Bite | `#f97316` | Medium | Conductor necking; elevated trace resistance | 4-wire Kelvin milliohm check |
| `2` | Open Circuit | `#dc2626` | Critical | Total signal / power delivery loss | DMM continuity / flying-probe test |
| `3` | Short | `#b91c1c` | Critical | Power rail bridge, logic contention, burnout | Hi-pot isolation test (IPC-TM-650) |
| `4` | Spur | `#eab308` | Medium | IPC clearance violation; dielectric breakdown | IPC-2221 spacing rule optical check |
| `5` | Spurious Copper | `#38bdf8` | Low | Parasitic capacitive coupling / loose debris | Megohmmeter insulation resistance test |

---

## 4. Database Schema (SQLite + SQLAlchemy)

### `inspections` Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `original_filename` (VARCHAR(255))
- `stored_image_path` (VARCHAR(500))
- `annotated_image_path` (VARCHAR(500), Nullable)
- `total_defects` (INTEGER, Default 0)
- `inspection_status` (VARCHAR(50), Default "completed")
- `model_version` (VARCHAR(50), Default "YOLO26n-v1.0")
- `confidence_threshold` (FLOAT, Default 0.25)
- `inference_time` (FLOAT, Default 0.0)
- `image_width` (INTEGER, Nullable)
- `image_height` (INTEGER, Nullable)
- `notes` (TEXT, Nullable)
- `created_at` (DATETIME, Default UTC now, Indexed)

### `detections` Table
- `id` (INTEGER, Primary Key, Auto-increment)
- `inspection_id` (INTEGER, Foreign Key referencing `inspections.id` ON DELETE CASCADE, Indexed)
- `class_id` (INTEGER, 0 to 5)
- `class_name` (VARCHAR(100))
- `confidence` (FLOAT, 0.0 to 1.0)
- `x1`, `y1`, `x2`, `y2` (FLOAT, bounding box coordinates)


---

## 5. Implementation Milestones Status

| Milestone | Scope | Status | Verification Artifact |
|---|---|---|---|
| **Milestone 1** | Project Foundation, FastAPI Backend, SQLite Models, React Architecture | **COMPLETED** | 100% Passing Tests, Dual CORS Setup |
| **Milestone 2** | DeepPCB Dataset Engineering, YOLO Conversion, Zero-Leakage Split | **COMPLETED** | `DATASET_GUIDE.md`, 10,013 BBoxes Verified |
| **Milestone 3** | Ultralytics YOLO Training, GPU Detection, Hyperparameter Pipeline | **COMPLETED** | `models/best.pt`, `models/training_summary.json` |
| **Milestone 4** | Detection Service, Singleton Model Loader, Color-Coded Overlays | **COMPLETED** | `POST /api/inspect`, `backend/annotated/` |
| **Milestone 5** | Frontend Integration, Interactive Canvas, History Audit Log | **COMPLETED** | React 18, Vite Production Build Verified |
| **Milestone 6** | ReportLab PDF Inspection Reports with IPC-A-600 Protocols | **COMPLETED** | `GET /api/inspections/{id}/report`, `backend/reports/` |
| **Milestone 7** | End-to-End Verification, Documentation & Hackathon Demo Guide | **COMPLETED** | 17/17 Pytest Green, `HACKATHON_DEMO_GUIDE.md` |

---

## 6. Official Test Split Benchmark Performance

Evaluated strictly on the untouched DeepPCB test split (`datasets/pcb_defects/images/test`):
- **Mean Average Precision (mAP@50):** 89.49%
- **COCO Strict Metric (mAP@50-95):** 56.73%
- **Overall Precision:** 85.89%
- **Overall Recall:** 84.68%
- **Neural Inference Speed:** 49.23 ms / image
