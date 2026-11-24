# CircuitDoctor - API Documentation

## 1. Overview & Base URL

The CircuitDoctor backend is a high-performance RESTful API built with **FastAPI**, **SQLAlchemy**, and **Ultralytics YOLO**.

- **Default Local Base URL:** `http://localhost:8000`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **ReDoc Interactive Reference:** `http://localhost:8000/redoc`
- **API Version:** `v1.0.0`
- **Prefix:** `/api`

---

## 2. Core Domain Principle: Visual Inspection vs. Electrical Fault Diagnosis

> [!IMPORTANT]
> All findings returned by CircuitDoctor endpoints represent **visual defect predictions** from surface optical imagery.
> The API explicitly delineates optical anomalies from electrical faults. Endpoints include specific non-destructive electrical testing recommendations (continuity, 4-wire Kelvin resistance, hi-pot isolation) to assist hardware engineers.

---

## 3. Endpoints Reference

### 3.1 Health & Hardware Status

#### `GET /api/health`
Checks system availability, compute hardware status, database connectivity, and loaded model weights.

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_status": "ready",
  "model_path": "C:\\Users\\Ayush\\OneDrive\\Documents\\CircuitDoctor\\models\\best.pt",
  "device": "cpu",
  "database_status": "connected",
  "timestamp": "2026-11-22T10:30:00Z"
}
```

---

### 3.2 Model Architecture & Evaluation Telemetry

#### `GET /api/model/info`
Returns complete neural network architecture metadata, GPU acceleration parameters, the 6 canonical DeepPCB classes, and actual evaluation metrics evaluated on the test partition.

**Response (`200 OK`):**
```json
{
  "model_name": "CircuitDoctor-YOLO",
  "model_architecture": "Ultralytics YOLO11n / YOLO26n",
  "model_version": "YOLO11n-PCB-v1.0",
  "model_status": "ready",
  "model_path": "models/best.pt",
  "weights_exist": true,
  "weights_size_bytes": 5613764,
  "device": "cpu",
  "cuda_available": false,
  "gpu_name": null,
  "total_gpu_memory_mb": null,
  "supported_classes": [
    {
      "id": 0,
      "name": "Missing Hole",
      "key": "missing_hole",
      "description": "Via or through-hole missing from required drill location.",
      "color_hex": "#ef4444",
      "severity": "critical",
      "electrical_risk": "Break in layer-to-layer interconnect or missing component pin mount.",
      "verification_advice": "Perform continuity check and optical coordinate measurement."
    },
    {
      "id": 1,
      "name": "Mouse Bite",
      "key": "mouse_bite",
      "description": "Erosion or nick along trace edges causing local necking.",
      "color_hex": "#f97316",
      "severity": "medium",
      "electrical_risk": "Reduced cross-sectional area leading to increased resistance.",
      "verification_advice": "Perform 4-wire milliohm resistance check across suspect trace."
    },
    {
      "id": 2,
      "name": "Open Circuit",
      "key": "open_circuit",
      "description": "Unintended break or discontinuity in conductive copper trace.",
      "color_hex": "#dc2626",
      "severity": "critical",
      "electrical_risk": "Total loss of signal propagation or power delivery.",
      "verification_advice": "Perform digital multimeter continuity / flying-probe electrical test."
    },
    {
      "id": 3,
      "name": "Short",
      "key": "short",
      "description": "Unintended copper bridging connecting two electrically distinct nets.",
      "color_hex": "#b91c1c",
      "severity": "critical",
      "electrical_risk": "Overcurrent damage, ground fault, or logic contention.",
      "verification_advice": "Perform isolation resistance / high-pot testing between adjacent nets."
    },
    {
      "id": 4,
      "name": "Spur",
      "key": "spur",
      "description": "Pointed copper protrusion projecting outwards from conductor trace.",
      "color_hex": "#eab308",
      "severity": "medium",
      "electrical_risk": "Reduced clearance distance; risk of dielectric breakdown.",
      "verification_advice": "Check minimum trace clearance spacing against IPC-2221 design rules."
    },
    {
      "id": 5,
      "name": "Spurious Copper",
      "key": "spurious_copper",
      "description": "Isolated residual copper island left behind after chemical etching.",
      "color_hex": "#38bdf8",
      "severity": "low",
      "electrical_risk": "Potential parasitic capacitance or debris migration.",
      "verification_advice": "Verify galvanic isolation from all adjacent functional nets."
    }
  ],
  "default_confidence_threshold": 0.25,
  "default_iou_threshold": 0.45,
  "training_metrics": { ... }
}
```

---

### 3.3 Dataset Information

#### `GET /api/dataset/info`
Returns metadata and split statistics for the DeepPCB dataset.

**Response (`200 OK`):**
```json
{
  "dataset_name": "DeepPCB",
  "source": "Tang et al., 2019 (Synthetic Defect Pairs)",
  "total_images": 1500,
  "total_annotations": 10013,
  "splits": {
    "train": { "images": 1068, "annotations": 7171, "percentage": 71.2 },
    "val": { "images": 320, "annotations": 2149, "percentage": 21.3 },
    "test": { "images": 112, "annotations": 693, "percentage": 7.5 }
  },
  "leakage_safe": true,
  "class_mapping_verified": true
}
```

---

### 3.4 Automated Optical Inspection (Inference)

#### `POST /api/inspect`
Uploads a PCB image, executes YOLO defect detection, saves color-coded bounding box overlays, and returns persistent inspection records.

**Request:** `multipart/form-data`
- `file`: Image file (`.jpg`, `.jpeg`, `.png`, max 25 MB)
- `confidence_threshold` *(optional, default: 0.25)*: Confidence filter (0.01 to 0.99)
- `iou_threshold` *(optional, default: 0.45)*: Non-maximum suppression IoU threshold

**Response (`201 Created`):**
```json
{
  "id": 1,
  "original_filename": "sample_pcb.jpg",
  "stored_image_path": "C:\\Users\\...\\backend\\uploads\\1732272800_sample_pcb.jpg",
  "annotated_image_path": "C:\\Users\\...\\backend\\annotated\\annotated_sample_pcb_1732272801.jpg",
  "total_defects": 2,
  "inspection_status": "fail",
  "model_version": "YOLO11n-PCB",
  "confidence_threshold": 0.25,
  "inference_time": 44.8,
  "image_width": 640,
  "image_height": 640,
  "created_at": "2026-11-22T10:32:00Z",
  "original_image_url": "/api/images/original/1",
  "annotated_image_url": "/api/images/annotated/1",
  "report_url": "/api/inspections/1/report",
  "detections": [
    {
      "id": 1,
      "inspection_id": 1,
      "class_id": 2,
      "class_name": "Open Circuit",
      "confidence": 0.892,
      "x1": 142,
      "y1": 210,
      "x2": 178,
      "y2": 244
    },
    {
      "id": 2,
      "inspection_id": 1,
      "class_id": 3,
      "class_name": "Short",
      "confidence": 0.764,
      "x1": 310,
      "y1": 405,
      "x2": 345,
      "y2": 438
    }
  ]
}
```

---

### 3.5 Inspection History & Audit Trail

#### `GET /api/inspections`
Retrieves past inspection records with pagination and filtering.

**Query Parameters:**
- `skip` *(int, default: 0)*
- `limit` *(int, default: 50, max: 200)*
- `defect_class` *(int, 0 to 5)*: Filter by defect class presence
- `status` *(string)*: `'pass'`, `'warning'`, or `'fail'`

#### `GET /api/inspections/{id}`
Returns full details of an inspection including all detection coordinates.

#### `DELETE /api/inspections/{id}`
Permanently deletes an inspection record, its detection items, and the stored image files.

---

### 3.6 PDF Report Generation

#### `GET /api/inspections/{id}/report`
Streams a publication-grade PDF inspection report built with ReportLab, including:
- Side-by-side original and annotated PCB imagery.
- Bounding box findings table with coordinates and confidence scores.
- Prominent engineering disclaimer detailing electrical verification protocols (IPC-A-600 standards).

---

### 3.7 Image Streaming

#### `GET /api/images/original/{id}`
Streams the original uploaded PCB photograph. Includes directory traversal protection.

#### `GET /api/images/annotated/{id}`
Streams the AI-annotated PCB photograph with color-coded bounding boxes and defect labels.
