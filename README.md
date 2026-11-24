# CircuitDoctor: AI-Powered PCB Defect Detection and Inspection Platform

> **Industrial Automated Optical Inspection (AOI) System for Printed Circuit Board Surface Defect Analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.165-teal.svg)](https://fastapi.tiangolo.com/)
[![React: 18](https://img.shields.io/badge/React-18.3-blue.svg)](https://react.dev/)
[![YOLO Architecture](https://img.shields.io/badge/YOLO-Ultralytics%20YOLO11n%2F26n-orange.svg)](https://github.com/ultralytics/ultralytics)
[![Test Suite](https://img.shields.io/badge/Tests-17%20Passed-brightgreen.svg)](backend/tests/)

---

## 1. Project Overview

Printed Circuit Boards (PCBs) are the physical foundation of modern electronics. Surface defects generated during chemical etching, laser drilling, and plating can cause critical functional failures. Manual visual inspection under microscopes is labor-intensive, error-prone, and inconsistent.

**CircuitDoctor** is a full-stack, AI-powered industrial inspection platform that automates the visual identification, localization, and classification of PCB manufacturing surface defects using computer vision and deep learning.

### The Optical vs. Electrical Distinction
CircuitDoctor distinguishes between visual optical detection and electrical fault diagnosis:
- **Visual AI predictions** pinpoint surface defects from photographic data.
- Optical AI **cannot confirm** internal layer shorts, high-resistance trace necking, or component failure.
- Every classified defect in CircuitDoctor includes specific **electrical verification recommendations** (e.g., 4-wire Kelvin resistance, continuity, or hi-pot isolation testing).

---

## 2. Core Defect Categories (DeepPCB Standard)

CircuitDoctor uses a single source of truth mapping for the 6 standard DeepPCB categories (`backend/app/core/defect_classes.py`):

| ID | Class Name | Severity | Primary Electrical Risk | Recommended Electrical Test |
|---|---|---|---|---|
| `0` | **Missing Hole** | Critical | Break in layer-to-layer interconnect or missing pin mount | Optical drill probe + continuity test |
| `1` | **Mouse Bite** | Medium | Localized conductor necking, elevated trace resistance | 4-wire Kelvin milliohm measurement |
| `2` | **Open Circuit** | Critical | Total loss of signal or power delivery along net | DMM continuity / flying-probe test |
| `3` | **Short** | Critical | Unintended copper bridge between distinct nets | Hi-pot isolation / resistance check |
| `4` | **Spur** | Medium | Reduced clearance distance; dielectric breakdown | IPC-2221 spacing verification |
| `5` | **Spurious Copper** | Low | Parasitic capacitance or FOD migration | Megohmmeter insulation testing |

---

## 3. Real Performance Benchmarks (Untouched Test Split)

Evaluated exclusively on the untouched DeepPCB test split (112 unseen images, 693 ground-truth defect instances, 0% cross-split design leakage):

| Metric | Score on Test Partition |
|---|---|
| **mAP@50 (Overall)** | **89.49%** |
| **mAP@50-95 (COCO Strict)** | **56.73%** |
| **Mean Precision** | **85.89%** |
| **Mean Recall** | **84.68%** |
| **Inference Latency** | **49.2 ms / image** |

### Per-Class Test Performance:
- **Spurious Copper:** 99.5% mAP@50 | 97.2% Precision | 99.0% Recall
- **Missing Hole:** 99.0% mAP@50 | 93.4% Precision | 96.3% Recall
- **Mouse Bite:** 97.4% mAP@50 | 89.8% Precision | 95.1% Recall
- **Spur:** 97.1% mAP@50 | 96.5% Precision | 81.2% Recall
- **Open Circuit:** 96.5% mAP@50 | 97.0% Precision | 80.6% Recall
- **Short:** 47.5% mAP@50 | 41.5% Precision | 55.8% Recall

---

## 4. Technology Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Lucide React, Recharts, Axios, React Router 7
- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, SQLite, ReportLab, OpenCV, Pillow
- **Machine Learning:** PyTorch, Ultralytics YOLO (YOLO11n / YOLO26n baseline), Transfer Learning
- **Dataset:** DeepPCB (1,500 test images, 1,500 template pairs; 10,013 bounding boxes; 71.2% Train, 21.3% Val, 7.5% Test)
- **Reporting:** ReportLab publication-grade PDF generation with visual evidence and IPC-A-600 electrical testing protocols

---

## 5. Quick Start: Running the Application

### Prerequisites
- Python 3.11
- Node.js (v18+) and npm

### 1. Start the Backend API Server
```powershell
# From project root
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### 2. Start the React Frontend
```powershell
cd frontend
npm.cmd run dev
```
- Web Application: `http://localhost:5173`

### 3. Run Automated Tests
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m pytest backend/tests/ -v
```

---

## 6. Project Documentation Directory

- [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) - Complete system architectural diagrams, database schemas, and service boundaries.
- [DATASET_GUIDE.md](DATASET_GUIDE.md) - DeepPCB dataset acquisition, coordinate conversion, and zero-leakage validation.
- [MODEL_TRAINING_GUIDE.md](MODEL_TRAINING_GUIDE.md) - YOLO training commands, hyperparameter configurations, and evaluation steps.
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Comprehensive REST endpoint specification with sample request/response payloads.
- [HACKATHON_DEMO_GUIDE.md](HACKATHON_DEMO_GUIDE.md) - Step-by-step judge demonstration script and technical Q&A.
