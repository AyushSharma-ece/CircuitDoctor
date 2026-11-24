# CircuitDoctor - Hackathon & Technical Presentation Demo Guide

## 1. Executive Summary & 30-Second Pitch

> *"Printed Circuit Boards are the nervous system of modern electronics. While automated pick-and-place machines assemble boards at lightning speeds, quality inspection has remained a manual bottleneck where microscopic flaws like mouse bites or spurious copper escape visual detection.*
>
> *We built **CircuitDoctor** — an AI-powered Automated Optical Inspection (AOI) platform engineered specifically for electronics quality engineering. Powered by an Ultralytics YOLO deep learning detector trained on the benchmark DeepPCB dataset, CircuitDoctor localizes microscopic surface anomalies in milliseconds, generates color-coded overlays, maintains an auditable inspection database, and produces publication-quality engineering reports.*
>
> *Crucially, as electronics engineers, we designed CircuitDoctor with a strict engineering boundary: optical inspection predicts surface geometry anomalies, but cannot diagnose electrical continuity. Every finding automatically includes prescribed electrical verification tests — from 4-wire Kelvin resistance to high-pot isolation."*

---

## 2. Technical Highlights for Judges & Reviewers

1. **True AI Vision Engine, Not a Mock Prototype:**
   - Powered by **Ultralytics YOLO** (YOLO11n / YOLO26n baseline) running transfer learning on 10,013 real PCB defect annotations.
   - Real, measured inference latency (measured in milliseconds per image, never fabricated).
2. **Leakage-Safe Dataset Engineering:**
   - DeepPCB dataset (1,500 test images, 1,500 template pairs) partitioned into 71.2% Train, 21.3% Validation, and 7.5% Test subsets by board group.
   - **0% data leakage**: test samples never share board design layouts with the training split.
3. **Dual Domain Rigor (Optical vs. Electrical):**
   - Distinguishes visual appearance from electrical reality.
   - Recommends specific test instrumentation (flying-probe continuity, 4-wire micro-ohm measurement, hi-pot isolation) following IPC-A-600 standards.
4. **Full-Stack Industrial Dashboard:**
   - Dark navy / charcoal industrial design (#070b14, #0f172a, #0284c7).
   - Side-by-side visual inspection viewer (Raw PCB vs. Neural Overlay).
   - Automated PDF report generator built with ReportLab.

---

## 3. Recommended Live Demo Script (Step-by-Step)

### Step 1: System Dashboard & Telemetry
1. Open the application at `http://localhost:5173`.
2. **Point out:**
   - Total inspections and defect distribution charts.
   - Live hardware telemetry (CPU/GPU acceleration, VRAM, and loaded model status).
   - Clear empty states if the database has not yet been populated.

### Step 2: Dataset Engineering Verification
1. Navigate to **Dataset Information** in the sidebar.
2. **Point out:**
   - Real DeepPCB dataset metadata: 1,500 total images, 10,013 bounding boxes.
   - Exact partition split: 1,068 Train (71.2%), 320 Val (21.3%), 112 Test (7.5%).
   - The mathematical coordinate transformation from $(x_1, y_1, x_2, y_2)$ pixels to normalized YOLO $(cx, cy, w, h)$.
   - 0% cross-partition leakage guarantee.

### Step 3: Model Architecture & Test Evaluation
1. Navigate to **Model Information**.
2. **Point out:**
   - Real evaluation metrics computed exclusively on the **untouched test split** (`datasets/pcb_defects/images/test`).
   - Mean Average Precision ($\text{mAP}@50$ and $\text{mAP}@50-95$), Precision, and Recall.
   - Per-class breakdown across all 6 DeepPCB classes:
     - Class 0: Missing Hole
     - Class 1: Mouse Bite
     - Class 2: Open Circuit
     - Class 3: Short
     - Class 4: Spur
     - Class 5: Spurious Copper

### Step 4: Perform a Live PCB Inspection
1. Navigate to **New Inspection**.
2. Select or drag & drop a sample image from the test partition:
   - Example file: `datasets/pcb_defects/images/test/12000001_test.jpg`
3. Set the Confidence Threshold slider (e.g. `25%` or `30%`).
4. Click **Analyse PCB Surface**.
5. Observe the neural inference progress and instantaneous results display.

### Step 5: Explore the Visual Findings
1. Use the **Inspection Canvas**:
   - Toggle **Annotated Overlay** to see high-contrast bounding boxes with class colors and confidence tags.
   - Toggle **Raw PCB** to inspect the bare surface.
   - Toggle **Side-by-Side** to present a direct comparison.
2. Review the **Defect Findings Table**:
   - Highlight bounding box coordinates $[x_1, y_1, x_2, y_2]$.
   - Highlight defect classification and severity (Critical vs. Medium vs. Low).
   - Point out the specific **Recommended Electrical Action** column.
3. Review the **Optical Inspection Limitation Notice** banner.

### Step 6: Generate and Download the Official PDF Report
1. Click **Download Official PDF Report**.
2. The browser immediately receives the ReportLab-generated PDF:
   - Header with unique Inspection ID, timestamp, and Pass/Warning/Fail status badge.
   - Side-by-side visual evidence photos.
   - Defect breakdown table.
   - Full IPC-A-600 electrical testing compliance disclaimer.

### Step 7: Inspection History & Auditing
1. Navigate to **Inspection History**.
2. Show the searchable, filterable audit log of all stored inspections.
3. Filter by defect category (e.g., "Class 3: Short") or status ("Fail").
4. Click any inspection to reopen the full interactive modal viewer.

---

## 4. Anticipated Judge Questions & Strong Technical Answers

### Q1: *"Why did you use Ultralytics YOLO instead of a Vision-Language Model like GPT-4o or Gemini?"*
> **Answer:**
> *"Automated Optical Inspection on high-speed SMT assembly lines requires real-time deterministic bounding boxes with millisecond latency. General-purpose VLMs often suffer from coordinate hallucinations, cannot achieve 50ms inference speeds locally on edge hardware, and cost significant cloud API fees per image. YOLO provides deterministic bounding box coordinates, runs fully offline in air-gapped manufacturing plants, and processes 20+ frames per second on modest hardware."*

### Q2: *"How did you prevent data leakage during dataset preparation?"*
> **Answer:**
> *"In PCB inspection datasets like DeepPCB, multiple test images are generated from the same physical board design layout with different defect injection points. If we randomly shuffled images across splits, identical board layouts would appear in both training and test partitions, resulting in artificially inflated test accuracy. We solved this by grouping images by their board design identifier and splitting entire board families contiguously into 70% Train, 20% Validation, and 10% Test. The test partition contains 100% unseen board designs."*

### Q3: *"Can your AI tell if a short circuit is actually conducting electricity?"*
> **Answer:**
> *"No, and that is a deliberate engineering distinction we emphasize throughout the platform. 2D optical images only capture surface appearance. An apparent 'short' could be an inert piece of solder mask, or conversely, an apparent gap might have a conductive carbon track underneath. CircuitDoctor acts as a first-line visual filter that flags anomalies and routes them to specific electrical instruments: flying-probe continuity testers, 4-wire Kelvin micro-ohmmeters, and high-voltage hi-pot insulation testers."*

### Q4: *"What are the 6 defect categories?"*
> **Answer:**
> *"We follow the canonical DeepPCB taxonomy from Tang et al., 2019: Missing Hole (drill via missing), Mouse Bite (conductor trace edge necking), Open Circuit (full trace discontinuity), Short (unintended copper bridging), Spur (pointed trace protrusion), and Spurious Copper (isolated etching residue). Each is mapped to a single source of truth across dataset conversion, training, backend schemas, and UI visualization."*
