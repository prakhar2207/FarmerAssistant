# 🌾 KrishiSaathi (कृषि साथी)
### Multimodal AI Agricultural Advisory & Agentic Farming Intelligence System
**भारतीय किसानों के लिए आधुनिक एजेंटिक एआई, कंप्यूटर विज़न एवं बहुभाषी कृषि निर्णय समर्थन प्रणाली**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4%2B-red.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 40/40 Passed](https://img.shields.io/badge/Tests-40%2F40%20Passed%20(100%25)-brightgreen.svg)]()

---

## 📖 Overview

**KrishiSaathi (कृषि साथी)** is an enterprise-grade, India-specific, Hindi-first and English multimodal agricultural advisory system. Designed specifically for Indian farmers and field agronomists, KrishiSaathi unifies **Conversational Agentic Graph Orchestration**, **PyTorch/YOLO Computer Vision foliar diagnostics**, **ICAR-grounded Retrieval-Augmented Generation (RAG)**, **Soil Health Card analytics**, and **Real-Time Weather Intelligence** into a clean, ChatGPT-style responsive user interface.

Unlike generic chatbots that answer farming queries blindly, KrishiSaathi operates through an explicit **9-node State Machine / Graph Orchestrator** (`app/core/graph.py`) that:
1. **Understands Natural Multimodal Inputs**: Hindi voice transcriptions, Devanagari text, Romanized Hinglish, English queries, foliar disease photos, and PDF/image Soil Health Cards.
2. **Clarifies Ambiguous Inquiries**: When key agronomic slots (crop name, variety, plant age, symptoms) are missing, it asks gentle, actionable counter-questions instead of guessing.
3. **Guarantees Scientific Safety**: Enforces strict CIBRC statutory bans on hazardous agrochemicals (e.g., Endosulfan, Monocrotophos, Phorate) and checks 48-hour rainfall probability before permitting foliar sprays or urea application.
4. **Verifiable Government & ICAR Grounding**: Emits auditable citations citing Indian Council of Agricultural Research institutes (IIWBR, NRRI, IIHR, CPRI) and Ministry schemes (PM-KISAN, PMFBY, KCC).
5. **Streams in Real-Time**: Streams responses via Server-Sent Events (SSE) with live progress badges, transparent agronomic reasoning thoughts, and clickable follow-up chips.

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │               Farmer Multi-Modal Interface             │
                                  │   (Devanagari Hindi / English Voice, Photos, Reports)  │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                                              ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │                    FastAPI Gateway                     │
                                  │     • SSE Stream: POST /api/chat/stream                │
                                  │     • REST Endpoints: /chat, /disease, /soil, /weather │
                                  │     • Magic-Byte File Validation & Rate Limiter        │
                                  └───────────────────────────┬────────────────────────────┘
                                                              │
                                                              ▼
                                  ┌────────────────────────────────────────────────────────┐
                                  │       Explicit Agent State Graph (app/core/graph.py)   │
                                  │  [Node 1: Intent & Slot Filling]                       │
                                  │        │                                               │
                                  │  [Node 2: Out-of-Domain Guard]                         │
                                  │        │                                               │
                                  │  [Node 3: Banned Chemical / Safety Guard]              │
                                  │        │                                               │
                                  │  [Node 4: Ambiguity Clarification]                     │
                                  │        │                                               │
                                  │  [Node 5: Agro-Climatic Context (Weather/Soil)]        │
                                  │        │                                               │
                                  │  [Node 6: Tool Execution Engine] ─────────────────┐    │
                                  │        │                                          │    │
                                  │  [Node 7: ICAR RAG Grounding Engine]              │    │
                                  │        │                                          │    │
                                  │  [Node 8: Weather / Rain Safety Post-Audit]       │    │
                                  │        │                                          │    │
                                  │  [Node 9: SSE Stream & Memory Persistence]        │    │
                                  └───────────────────────────┬───────────────────────┘    │
                                                              │                            │
                     ┌────────────────────────────────────────┴─────────────────────┐      │
                     ▼                                                              ▼      │
    ┌──────────────────────────────────┐                           ┌─────────────────────┐ │
    │    Relational DB (SQLAlchemy)    │                           │    External APIs    │ │
    │  • SQLite: krishi_saathi.db      │                           │  • Open-Meteo Weather│ │
    │  • Conversations & Chat History  │                           │  • GPS Geocoding    │ │
    │  • Soil Reports & Disease Logs   │                           │  • ICAR Data Store  │ │
    └──────────────────────────────────┘                           └─────────────────────┘ │
                                                                                           │
    ┌──────────────────────────────────────────────────────────────────────────────────────┘
    │ Specialized Agricultural Tools:
    ├── 📸 YOLO Foliar Vision: 3-tier confidence leaf diagnostics with bounding box coordinates
    ├── 🧪 Soil Analyzer: ICAR-grounded health index (0-100), deficiency identification & lab finder
    ├── 🌱 Crop Recommender: RandomForest ML model with explainable feature importance
    ├── 💊 Fertilizer Engine: Stage-wise INM schedule in practical farmer units (50kg bags)
    ├── 🏛️ Scheme Catalog: Direct benefit schemes eligibility checker (PM-KISAN, KCC, PMFBY)
    └── 🌦️ Weather Intelligence: Agrometeorological spray/irrigation/frost risk advisories
```

---

## 🔬 Scientific Foundations & Research Compliance

KrishiSaathi synthesizes validated architectures from peer-reviewed agricultural AI research:

1. **Krishi Sathi (BharatGen / IIT Bombay - arXiv:2508.03719)**:
   - Dynamic intent slot filling and missing-slot clarification dialogues in colloquial Hindi.
   - Grounded RAG incorporating domain-specific agricultural extensions.
2. **Farmer.Chat (Microsoft Research & Digital Green - arXiv:2409.08916)**:
   - Field-tested against 15,000+ real farmer interactions: 50%+ queries focus on crop diseases and nutrient scheduling.
   - Readability at the grassroots level: outputs dosages in practical units (50 kg बोरी, 15 L नैपसैक स्प्रेयर टंकी).
   - Zero hallucinations on banned pesticides.
3. **AgriGPT-VL (Zhejiang University - arXiv:2510.04002)**:
   - Multimodal foliar lesion segmentation (chlorosis halos, necrotic spots) linked directly to pathogen life-cycles.

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+ (tested up to Python 3.14 on Windows and Linux)
- Modern web browser with Web Speech API support (Google Chrome, Microsoft Edge)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/prakhar2207/FarmerAssistant.git
cd FarmerAssistant

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize Database & Run
```bash
# Initialize SQLite relational database schema
python main.py init-db

# Launch application server
python main.py run --host 0.0.0.0 --port 8000 --reload
```

Access the application in your browser at: **`http://localhost:8000`**

---

## 🐳 Docker Deployment

Run KrishiSaathi in an isolated, production-ready container:

```bash
# Build and start via Docker Compose
docker-compose up -d --build

# Inspect container health
docker ps -f name=krishisaathi_app

# Access API healthcheck
curl http://localhost:8000/api/health
```

---

## 🧪 Comprehensive Test Suite & AI Benchmark

KrishiSaathi features a comprehensive automated test suite with **40 test cases** achieving a **100% pass rate**.

### Running Tests
```bash
# Run full test suite
pytest -v tests/

# Run AI Evaluation Benchmark (28 realistic farmer scenarios)
python main.py eval
```

### Test Suite Breakdown:
| Test File | Description | Status |
| :--- | :--- | :---: |
| `tests/test_scenarios_1_to_12.py` | 12 end-to-end multi-turn & multimodal farmer scenarios | ✅ 12/12 Passed |
| `tests/test_eval_benchmark.py` | 28 benchmark scenarios from `eval_dataset.json` | ✅ 2/2 Passed |
| `tests/test_security_and_adversarial.py` | Magic bytes, rate limiting, prompt injection & banned chemicals | ✅ 4/4 Passed |
| `tests/test_api.py` | FastAPI REST & SSE endpoints integration | ✅ 6/6 Passed |
| `tests/test_orchestrator.py` | Graph state transitions & slot clarification in Hindi/English | ✅ 5/5 Passed |
| `tests/test_soil.py` | Acidic/alkaline analysis, amendment dosage & KVK lab finder | ✅ 3/3 Passed |
| `tests/test_disease.py` | Synthetic leaf foliar lesion inference & spray weather warning | ✅ 1/1 Passed |
| `tests/test_crop_recommender.py` | RandomForest ML crop predictions & feature importance | ✅ 2/2 Passed |
| `tests/test_weather.py` | Open-Meteo caching, agro-rules & district geocoding | ✅ 3/3 Passed |
| `tests/test_safety.py` | CIBRC banned chemical detection & rain probability safety | ✅ 2/2 Passed |
| **Total** | **All 40 Automated Unit, Scenario & Security Tests** | **✅ 40/40 (100%)** |

---

## 📡 API Reference

### Core Endpoints

#### 1. `POST /api/chat/stream` (Server-Sent Events)
Streams response chunks, real-time status badges, and thought steps to the frontend.
```json
// Request
{
  "message": "गेहूं में पहली खाद कब और कितनी मात्रा में डालनी चाहिए?",
  "session_id": "session_farmer_01",
  "farmer_id": "farmer_lucknow_01",
  "lang": "hi"
}
```

#### 2. `POST /api/disease/analyze` (Foliar Computer Vision)
Uploads leaf photography (`multipart/form-data`) with optional `crop_hint` and `rain_forecast`.
Returns:
- `is_leaf` (bool): Rejection flag if non-leaf image uploaded.
- `disease_name_hindi` & `disease_name_en`.
- `confidence_score` (0-100) and `confidence_tier` (`high`, `medium`, `low`).
- `bounding_boxes`: `[{x1, y1, x2, y2, label, confidence}]`.
- `immediate_cultural_action`, `organic_ipm_remedy`, and `chemical_solution`.
- `weather_spray_advisory`: Rain-delayed warning if rain expected in 48h.

#### 3. `POST /api/soil/analyze` (Soil Intelligence)
Takes soil metrics (`ph`, `ec`, `oc`, `n`, `p`, `k`, `zn`, `fe`, `s`, `state`, `district`).
Returns:
- `health_score` (0-100) with transparent score breakdown.
- `deficiencies` & `excesses` with agronomic explanations.
- `amendments`: Specific doses of lime (चूना), gypsum (जिप्सम), or organic FYM.
- `nearby_labs`: Geo-located ICAR / KVK government soil testing laboratories.

#### 4. `POST /api/crop/recommend` (Crop Recommender)
Accepts soil conditions and climatic parameters, returning top 3 suitable crops with seasonal risk assessments and rationale.

#### 5. `GET /api/schemes` (Government Schemes)
Searches and filters government agricultural welfare schemes (PM-KISAN, PMFBY, KCC, PM-KUSUM) based on state and landholding size.

#### 6. `GET /api/health` and `GET /api/readiness`
Provides container health status, hardware acceleration device (CUDA/CPU), and database connectivity status.

---

## 🛡️ Agricultural Safety & CIBRC Compliance

KrishiSaathi enforces non-negotiable safety guardrails:
* **Statutory Chemical Bans**: Refuses and redirects banned organophosphates and hazardous chemicals (Monocrotophos, Endosulfan, Phorate, Methyl Parathion, Paraquat Dichloride, DDT, Lindane) to safe CIBRC-approved alternatives and bio-pesticides.
* **Weather-Triggered Spray Interception**: Warns farmers against foliar pesticide/fungicide application when rain probability $\ge 30\%$ or wind speed $> 20$ km/h.
* **Nitrogen Leaching Prevention**: Halts urea top-dressing during heavy rain forecasts to eliminate environmental pollution and monetary waste.
* **KVK Escalation Protocols**: Whenever leaf damage exceeds 30% or confidence is low, provides toll-free Kisan Call Centre helpline (**1800-180-1551**) and local KVK contacts.

---

## 🤝 Contributing & License

Contributions are welcome! Please run `pytest` before submitting pull requests.

Released under the [MIT License](LICENSE).
