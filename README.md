# SmartBio – Underwater Biofouling Growth Monitoring & Cleaning Alert System

> **Academic ECE Mini-Project Prototype**  
> An intelligent computer-vision and decision support web platform for vessel hull biofouling assessment, growth rate tracking, and predictive cleaning alerts — requiring **no specialized underwater cameras**.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [System Architecture](#3-system-architecture)
4. [Tech Stack](#4-tech-stack)
5. [Folder Structure](#5-folder-structure)
6. [Installation Prerequisites](#6-installation-prerequisites)
7. [Backend Setup](#7-backend-setup)
8. [Frontend Setup](#8-frontend-setup)
9. [Database Setup & Migrations](#9-database-setup--migrations)
10. [Run Commands](#10-run-commands)
11. [Demo Mode Explanation](#11-demo-mode-explanation)
12. [AI Model Integration Instructions](#12-ai-model-integration-instructions)
13. [API Documentation](#13-api-documentation)
14. [Prototype Limitations](#14-prototype-limitations)
15. [Future Improvements](#15-future-improvements)

---

## 1. Project Overview

Ship hull biofouling (the accumulation of micro-algae, barnacles, tubeworms, and macro-algae on immersed surfaces) increases hydrodynamic drag by up to 40%, inflating fuel consumption and greenhouse gas emissions. Traditional biofouling inspection mandates costly drydocking or specialized underwater remotely operated vehicles (ROVs) and divers.

**SmartBio** overcomes this barrier by allowing shipmasters, port inspectors, or maintenance engineers to upload ordinary vessel hull photos taken from mobile phones, quaysides, service boats, or drone cameras.

The platform provides an end-to-end decision workflow:
$$\text{Mobile/Laptop Upload} \rightarrow \text{OpenCV Processing} \rightarrow \text{Coverage \%} \rightarrow \text{Severity} \rightarrow \text{Store Audit} \rightarrow \text{Compare Prior Audits} \rightarrow \text{Calculate Growth} \rightarrow \text{Cleaning Advisory Alert}$$

### Core Academic Novelty: Temporal Growth Monitoring & Decision Support
SmartBio is **not just a simple image classifier**. Its primary novelty lies in tracking temporal biofouling progression across sequential inspections on each vessel, calculating:
* **Absolute Growth**: $\text{Current Coverage} - \text{Previous Coverage}$ (measured in percentage points, `pp`).
* **Relative Growth Rate**: $\left(\frac{\text{Current} - \text{Previous}}{\text{Previous}}\right) \times 100\%$.
* **Predictive Cleaning Alerts**: Recommending cleaning reviews when thresholds or rapid growth rates are triggered.

---

## 2. Key Features

* 📱 **Mobile & Laptop Image Ingestion**: Responsive Android/iOS mobile camera capture (`capture="environment"`) and desktop drag-and-drop file upload.
* 🔬 **Computer Vision Biofouling Estimation**: Multi-stage OpenCV pipeline utilizing HSV colorimetry, CLAHE contrast enhancement, Laplacian texture gradient filtering, morphology, and connected components.
* 📊 **Coverage & Severity Classification**: Calculates exact fouling pixel ratio against analyzable hull area with project-defined severity tiers:
  * **0% – 10%**: `LOW` 🟢
  * **10% – 30%**: `MEDIUM` 🟡
  * **30% – 50%**: `HIGH` 🔴
  * **> 50%**: `VERY HIGH` 🔴
* 📈 **Temporal Growth Charts**: Interactive Recharts time-series line graph illustrating historical coverage progression against advisory threshold reference lines.
* 🚨 **Intelligent Cleaning Review Alerts**: Formulates non-coercive, risk-calibrated decision guidance (Routine Monitoring, Frequent Monitoring, or Cleaning Review Recommended). Detects rapid growth if expansion $\ge 5.0\text{ pp}$.
* 🔍 **Side-by-Side Comparative Analysis**: Chronologically pairs any two inspections to inspect differential change, overlay shifts, and severity transitions.
* 📋 **Academic Inspection Reports**: Formats and exports printable audits with disclaimers, high-resolution original vs. processed images, and comparative metrics.
* ⚓ **Fleet Vessel Management**: Multi-vessel support allowing fleet operators to maintain dedicated audit histories for each vessel.
* 🗄️ **Zero-Setup Demo Data**: One-click generation of realistic academic demo timeline data (8% → 14% → 23% → 34% → 42%) with synthetic hull imagery and masks.

---

## 3. System Architecture

```
                 +-----------------------------------------------+
                 |             Mobile / Laptop Browser           |
                 |      (React + Vite + Tailwind CSS + Recharts) |
                 +-----------------------+-----------------------+
                                         |  REST API & Image Uploads
                                         v
                 +-----------------------------------------------+
                 |             FastAPI Backend Server            |
                 |              (Python 3.11 / Uvicorn)          |
                 +-------+-------------------------------+-------+
                         |                               |
          +--------------v--------------+ +--------------v--------------+
          |     OpenCV Demo Analyzer    | |    AI Model Analyzer        |
          |  - CLAHE contrast           | |  - YOLOv8-seg loader        |
          |  - HSV color segmentation   | |  - Auto-fallback to OpenCV  |
          |  - Laplacian texture filter | |    if weights absent        |
          |  - Morphological closing    | +-----------------------------+
          |  - Connected components     |
          +--------------+--------------+
                         | Processed Images & Masks
                         v
     +-------------------+--------------------+--------------------+
     |                                        |                    |
     v                                        v                    v
+------------------+                 +-----------------+  +-----------------+
| SQLite Database  |                 | /uploads/       |  | /processed/     |
| (SQLAlchemy ORM) |                 | Raw Hull Photos |  | Overlays & Masks|
+------------------+                 +-----------------+  +-----------------+
```

---

## 4. Tech Stack

### Frontend
* **React 19** with **Vite 6** (Modern, ultra-fast development and build pipeline)
* **Tailwind CSS 3** (Custom marine-tech color palette and mobile responsive layout)
* **Recharts** (Interactive time-series area/line charts with custom tooltips)
* **React Router DOM 7** (Client-side routing across 8 dedicated pages)
* **Lucide React** (Consistent marine, telemetry, and status iconography)

### Backend
* **Python 3.11**
* **FastAPI** (High-performance asynchronous REST API)
* **Uvicorn** (ASGI production server)
* **Pydantic v2** (Strict schema validation and serialization)
* **SQLAlchemy 2.0** (Relational ORM for SQLite)
* **python-multipart** (Safe streaming multipart file ingestion)

### Image Processing & Computer Vision
* **OpenCV (opencv-python-headless)** (Multi-spectral HSV filtering, CLAHE, Laplacian morphology)
* **NumPy** (Vectorized matrix operations and masking)
* **Pillow (PIL)** (Image integrity verification and security checks)

---

## 5. Folder Structure

```
mini peojecr/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py           # REST endpoints (health, analyze, vessels, etc.)
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── session.py          # SQLite engine and session factory
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── vessel.py           # Vessel SQLAlchemy model
│   │   │   └── inspection.py       # Inspection SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py          # Pydantic validation schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── alert_service.py    # Severity classification & growth calculations
│   │   │   └── report_service.py   # Formal audit report builder
│   │   ├── analyzers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Abstract base analyzer
│   │   │   ├── opencv_analyzer.py  # Demo Mode CV pipeline
│   │   │   └── ai_analyzer.py      # AI model loader with automatic fallback
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── file_utils.py       # Safe UUID storage & path traversal guard
│   │   ├── seed_demo_helper.py     # Synthetic imagery and demo dataset generator
│   │   ├── config.py               # Configurable thresholds & storage limits
│   │   └── main.py                 # FastAPI application and CORS setup
│   ├── uploads/                    # Secure local store for original uploads
│   ├── processed/                  # Generated overlays and binary masks
│   ├── seed_data.py                # Standalone CLI seeding script
│   ├── test_api.py                 # Automated backend test suite
│   ├── requirements.txt            # Python dependencies
│   └── venv/                       # Dedicated Python 3.11 virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Top navigation with mobile drawer
│   │   │   ├── Sidebar.jsx         # Desktop sidebar navigation
│   │   │   ├── DashboardCard.jsx   # Marine metric cards
│   │   │   ├── UploadBox.jsx       # Drag & drop and mobile camera capture
│   │   │   ├── ImagePreview.jsx    # Tabbed/split view for original, overlay, mask
│   │   │   ├── CoverageCard.jsx    # Circular/horizontal progress gauge
│   │   │   ├── SeverityBadge.jsx   # LOW, MEDIUM, HIGH, VERY HIGH badges
│   │   │   ├── GrowthChart.jsx     # Recharts biofouling growth trend
│   │   │   ├── InspectionTable.jsx # Filterable table (Vessel, Date, Severity)
│   │   │   ├── ComparisonCard.jsx  # Side-by-side differential comparison
│   │   │   ├── AlertCard.jsx       # Cleaning review decision card
│   │   │   ├── Toast.jsx           # Notification toast
│   │   │   ├── Modal.jsx           # Accessible modal dialog
│   │   │   ├── LoadingSpinner.jsx  # Animated marine spinner
│   │   │   ├── EmptyState.jsx      # Clean empty state view
│   │   │   └── ErrorState.jsx      # Error handling view
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx     # Hero, workflow diagram, feature cards
│   │   │   ├── Dashboard.jsx       # Metrics, growth chart, recent audits
│   │   │   ├── UploadAnalyze.jsx   # Upload & analyze page
│   │   │   ├── AnalysisResult.jsx  # Inspection detail, cleaning alert, report
│   │   │   ├── InspectionHistory.jsx # Searchable audit registry
│   │   │   ├── Comparison.jsx      # Side-by-side comparison page
│   │   │   ├── VesselManagement.jsx# Fleet directory and vessel creation
│   │   │   └── Settings.jsx        # Prototype calibration & demo data manager
│   │   ├── services/
│   │   │   └── api.js              # Fetch client with base URL resolution
│   │   ├── utils/
│   │   │   └── formatters.js       # Date, growth, and severity formatters
│   │   ├── App.jsx                 # Router configuration
│   │   ├── main.jsx                # Application root
│   │   └── index.css               # Tailwind CSS directives
│   ├── package.json
│   ├── vite.config.js              # Dev proxy configuration for /api and /uploads
│   └── tailwind.config.js          # Marine color theme extension
├── model/
│   ├── README.md                   # AI model integration guide
│   └── weights/                    # Directory for custom YOLO weights (.pt, .onnx)
├── docs/
│   └── README.md                   # Mirrored comprehensive documentation
└── README.md
```

---

## 6. Installation Prerequisites

* **Node.js**: v18.0 or higher (v24.x tested)
* **Python**: v3.10 or v3.11 (Python 3.11.5 tested)
* **Operating System**: Windows, Linux, or macOS

---

## 7. Backend Setup

1. Open a terminal in the project directory:
   ```bash
   cd backend
   ```
2. Activate or initialize the virtual environment:
   * On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * On Windows (Command Prompt):
     ```cmd
     venv\Scripts\activate.bat
     ```
   * On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 8. Frontend Setup

1. Open another terminal in the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Optional environment configuration:
   Create a `.env` file if deploying to a non-default host:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```
   *(By default, the Vite development proxy forwards all `/api`, `/uploads`, and `/processed` requests to port 8000 automatically).*

---

## 9. Database Setup & Migrations

SmartBio uses **SQLite** with SQLAlchemy ORM.
Database tables are automatically created on first server launch.

To initialize or seed the database manually with the academic demonstration dataset:
```bash
backend\venv\Scripts\python.exe backend\seed_data.py
```

This seeds:
* Vessel: `MV Ocean Voyager` (Container Cargo Carrier)
* 5 sequential inspections spanning 5 weeks:
  * 2026-08-20: **8.0%** (LOW)
  * 2026-08-27: **14.0%** (MEDIUM, +6.0 pp)
  * 2026-09-03: **23.0%** (MEDIUM, +9.0 pp)
  * 2026-09-10: **34.0%** (HIGH, +11.0 pp)
  * 2026-09-17: **42.0%** (HIGH, +8.0 pp)
* Generates realistic synthetic hull photos, segmented overlays, and binary masks.

---

## 10. Run Commands

### Starting the Backend Server
From the project root:
```bash
backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
* Backend URL: `http://127.0.0.1:8000`
* Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

### Starting the Frontend Development Server
From the `frontend` directory:
```bash
npm run dev
```
* Frontend URL: `http://localhost:5173`

---

## 11. Demo Mode Explanation

SmartBio is designed so that **no deep-learning weights or GPU are required** for demonstrations.

The OpenCV-based Demo Mode processes images as follows:
1. **Resolution Normalization**: Standardizes dimensions while preserving aspect ratio.
2. **Analyzable Hull Region Masking**: Excludes severe specular glares and sky regions.
3. **HSV Colorimetry**: Filters typical chlorophyte/algae green signatures ($H \in [25, 90]$) and organic brown biofilm clusters ($H \in [0, 25]$).
4. **CLAHE Contrast Equalization**: Balances underwater light attenuation and murky turbidity.
5. **Laplacian Texture Energy**: Quantifies high-frequency surface roughness to separate clean painted steel from encrustations (barnacles, tubeworms).
6. **Morphological Filtering**: Consolidates organism clusters via morphological closing and eliminates isolated camera noise via opening.
7. **Connected Components Analysis**: Filters speckles smaller than 15 pixels.
8. **Coverage Calculation**:
   $$\text{Coverage \%} = \frac{\text{Suspected Fouling Pixels}}{\text{Analyzable Hull Pixels}} \times 100$$
9. **Visual Output**: Produces an amber/cyan highlighted overlay with bounding cluster contours and a binary mask image.
10. **Ethical Labeling**: Results are explicitly tagged: **"Demo Computer-Vision Estimate"**. The system does not falsely claim confirmed biological species classification.

---

## 12. AI Model Integration Instructions

SmartBio has an extensible two-tier analyzer interface (`BaseAnalyzer`).

```
              ┌─────────────────────┐
              │     BaseAnalyzer    │
              └──────────┬──────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
┌─────────▼───────────┐       ┌─────────▼───────────┐
│   OpenCVAnalyzer    │       │   AIModelAnalyzer   │
│     (Demo Mode)     │       │   (YOLO / SegNet)   │
└─────────────────────┘       └─────────┬───────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │   Weights File Detected?    │
                         ├──────────────┬──────────────┤
                         │     YES      │      NO      │
                         │              │  (Fallback)  │
                         ▼              ▼              │
                  [Run YOLO Net]   [OpenCVAnalyzer] ◄──┘
```

To connect a trained YOLO model (e.g. YOLOv8x-seg trained on marine biofouling):

1. **Place Weights in `model/weights/`**:
   Copy your `.pt` or `.onnx` weights into the `model/weights/` directory.
2. **Install Ultralytics**:
   ```bash
   backend\venv\Scripts\pip.exe install ultralytics
   ```
3. **Uncomment Model Inference**:
   In `backend/app/analyzers/ai_analyzer.py`, uncomment the YOLO loader:
   ```python
   from ultralytics import YOLO
   model = YOLO(str(self.weights_path))
   results = model(str(image_path))
   ```
4. **Automatic Fallback Guarantee**:
   If no weights are placed in `model/weights/`, the backend automatically catches the condition, runs the OpenCV pipeline, and provides an alert banner:
   *"AI model unavailable — switched to Demo Mode."*

---

## 13. API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and AI model availability |
| `GET` | `/api/thresholds` | Configurable severity thresholds and project disclaimer |
| `GET` | `/api/vessels` | List all vessels with latest coverage and audit count |
| `POST` | `/api/vessels` | Register a new vessel (`vessel_name`, `vessel_type`, `notes`) |
| `GET` | `/api/vessels/{id}` | Detailed vessel information |
| `GET` | `/api/vessels/{id}/growth` | Chronological time-series for Recharts with calculated growth |
| `POST` | `/api/analyze` | Multipart image upload. Returns coverage %, severity, recommendation, overlay URL, and mask URL |
| `POST` | `/api/inspections` | Permanently saves an audit record to the database |
| `GET` | `/api/inspections` | Query audits with filters (`vessel_id`, `severity`, `start_date`, `end_date`) |
| `GET` | `/api/inspections/{id}` | Complete inspection detail with prior comparative metrics |
| `DELETE` | `/api/inspections/{id}` | Safely deletes record and associated disk imagery |
| `GET` | `/api/compare` | Differential analysis (`?previous_id=X&current_id=Y`) |
| `GET` | `/api/report/{id}` | Structured data payload for printable inspection reports |
| `POST` | `/api/seed-demo` | Seeds 5-week academic demonstration dataset |

---

## 14. Prototype Limitations

* **Lighting Sensitivity**: Strong surface glare, underwater turbidity, or silty harbor water can affect color-based thresholding.
* **Species Distinction**: The OpenCV demo algorithm estimates total cluster surface area rather than differentiating macro-algal slime from calcareous acorn barnacles.
* **Advisory Nature**: Severity classifications and cleaning recommendations are project-defined prototype estimations designed for academic demonstration and do not constitute certified naval architecture or drydock cleaning mandates.

---

## 15. Future Improvements

* **Multi-Class Biological Segmentation**: Train a YOLOv9-seg model to classify specific taxa (e.g. Slime Biofilm, Green Algae, Brown Algae, Hydroids, Barnacles, Tubeworms, Mussels).
* **3D Hull Reconstruction**: Integrate photogrammetry (Structure-from-Motion) to map 2D inspection photos onto a complete 3D digital twin of the vessel hull.
* **Fuel Penalty Calculator**: Correlate biofouling coverage percentage with ITTC (International Towing Tank Conference) empirical equations to estimate ship drag penalty and excess fuel consumption in metric tons.
* **Automated Cleaning Schedule Forecasting**: Utilize ARIMA or Long Short-Term Memory (LSTM) recurrent neural networks to predict exact calendar dates when biofouling will cross the 30% cleaning threshold.
