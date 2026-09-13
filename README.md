# 🌾 KrishiSaathi (कृषि साथी)
### Hindi AI Agricultural Advisory & Agentic Farming Intelligence System
**भारतीय किसानों के लिए आधुनिक एजेंटिक एआई एवं बहुभाषी कृषि निर्णय समर्थन प्रणाली**

---

## 📖 Overview

**KrishiSaathi** is an end-to-end, Hindi-first, agentic agricultural advisory platform tailored specifically for Indian farmers. It unifies cutting-edge research across conversational dialogue management, machine learning for crop recommendation, computer vision for plant disease diagnosis, soil report analytics, and real-time meteorological intelligence into a single, user-friendly farming assistant.

Unlike traditional static chatbots that answer one-off questions blindly, KrishiSaathi implements an **Intent-Aware, Multi-Turn Agentic Pipeline** that:
1. Progressively asks clarifying questions in Hindi when crucial details (crop variety, sowing time, soil condition) are missing.
2. Integrates real-time weather and forecast from Open-Meteo to prevent hazardous spraying or fertilizer wastage before rains.
3. Diagnoses crop leaf diseases using computer vision and provides CIBRC-safe chemical, biological (IPM), and organic remedies.
4. Analyzes Soil Health Cards (pH, NPK, OC, micronutrients) and directs farmers to nearby government testing laboratories.
5. Employs strict agricultural guardrails to block banned or hazardous agrochemicals (e.g., Endosulfan, Monocrotophos, Phorate).

---

## 🔬 Research Foundations

KrishiSaathi synthesizes findings and architectural patterns from four seminal research works:

1. **Krishi Sathi (BharatGen / IIT Bombay - arXiv:2508.03719)**:
   - *Multi-turn dialogue & intent-slot filling*: Dynamically detects missing slots and generates counter-questions in simple Hindi (e.g., *"आप किस मौसम में प्याज की रोपाई कर रहे हैं और कौन सी किस्म है?"*).
   - *Context-enriched RAG*: Combines user slots with curated ICAR / KVK knowledge bases.

2. **Farmer.Chat (Microsoft Research & Digital Green - arXiv:2409.08916)**:
   - *Tested with 15,000+ farmers & 300,000+ queries*: Pests & Diseases (#1) and Soil & Fertilizer (#2) account for over 50% of real queries.
   - *Simplicity & readability*: Translates technical kg/ha into practical farmer units (e.g., 50kg बोरी/कट्टा, 15-लीटर स्प्रेयर टंकी).
   - *Clickable follow-up prompt chips*: Boosts farmer engagement and eliminates typing friction.
   - *Strict banned chemicals screening*.

3. **Complete 20-Step Pipeline Architecture**:
   - Implements the complete pipeline: Multi-modal inputs $\to$ Vision analysis $\to$ Context builder $\to$ Auto-data weather layer $\to$ Clarification loop $\to$ Soil intelligence & labs $\to$ Data fusion $\to$ Query builder $\to$ RAG $\to$ Reasoning $\to$ Safe Hindi speech/text output.

4. **AgriGPT-VL (Zhejiang University - arXiv:2510.04002)**:
   - Visual feature grounding (chlorosis, necrotic spots, lesion patterns) coupled with multi-step agronomic deduction and weather constraints.

---

## 🏗️ System Architecture

```
                       ┌────────────────────────────────────────┐
                       │          Farmer User Interface         │
                       │    (Hindi Voice, Text, Photos, Soil)   │
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │            FastAPI Gateway             │
                       │   (/api/chat, /api/disease, /api/crop, │
                       │    /api/soil, /api/weather, /api/schemes)│
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │        Agentic AI Orchestrator         │
                       │  • Multi-turn Intent & Slot Detector   │
                       │  • Counter-Question Clarification      │
                       │  • Location & Weather Fusion           │
                       └───────────────────┬────────────────────┘
                                           │
       ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
       ▼                   ▼                               ▼                   ▼
┌───────────────┐   ┌───────────────┐               ┌───────────────┐   ┌───────────────┐
│ Weather Tool  │   │ Disease Vision│               │ Soil Analyzer │   │ Crop Predictor│
│ (Open-Meteo & │   │ (PyTorch Leaf │               │ (SHC + Govt   │   │ (RandomForest │
│ Agri-Alerts)  │   │  Diagnostics) │               │  Lab Locator) │   │  22 Crops)    │
└───────┬───────┘   └───────┬───────┘               └───────┬───────┘   └───────┬───────┘
        │                   │                               │                   │
        └───────────────────┼───────────────────────────────┴───────────────────┘
                            ▼
        ┌───────────────────────────────────────────────────────┐
        │         Fertilizer & IPM Pest Advisory Engine         │
        │  • INM Schedules (DAP, Urea, MOP in 50kg bags)        │
        │  • Biological Controls & Jeevamrut / Neemastra        │
        │  • Rain & Wind Spray Safety Constraints               │
        └───────────────────────────┬───────────────────────────┘
                                    ▼
        ┌───────────────────────────────────────────────────────┐
        │           Authoritative ICAR / KVK RAG Base           │
        │  • Verified Packages of Practices & Schemes (PM-KISAN)│
        │  • Source Citations & Transparent Grounding           │
        └───────────────────────────┬───────────────────────────┘
                                    ▼
        ┌───────────────────────────────────────────────────────┐
        │             Safety, CIBRC & Trust Filter              │
        │  • Redaction of banned chemicals (Endosulfan, etc.)   │
        │  • KVK Escalation & Farmer Disclaimers                │
        └───────────────────────────┬───────────────────────────┘
                                    ▼
        ┌───────────────────────────────────────────────────────┐
        │          Localized Multi-Modal Hindi Output           │
        │  • Conversational Devanagari Hindi Text               │
        │  • Web Speech Audio Playback (TTS)                    │
        │  • Clickable Follow-Up Suggestions                    │
        └───────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14 with CUDA acceleration)
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Installation
```bash
# 1. Activate environment
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the FastAPI web application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to: **`http://localhost:8000`**

---

## 🧪 Running Automated Tests

KrishiSaathi comes with a full automated test suite verifying all 20 pipeline steps:

```bash
.\venv\Scripts\pytest.exe -v tests/
```

### Test Coverage:
* `tests/test_weather.py`: Location resolution, live Open-Meteo weather fetch, and agricultural advisories (spray safety, frost warning, fungal humidity alert).
* `tests/test_soil.py`: Acidic/alkaline pH interpretation, nutrient deficiency detection, soil amendments, and government lab locator.
* `tests/test_crop_recommender.py`: ML Random Forest model inference, seasonal compatibility, and top-3 crop suggestions.
* `tests/test_disease.py`: Leaf image preprocessing, foliar symptom classification, and weather spray alert verification.
* `tests/test_safety.py`: CIBRC banned chemical detection and rain spray constraints.
* `tests/test_orchestrator.py`: Multi-turn intent detection, missing slot clarification flow, and end-to-end responses.
* `tests/test_api.py`: FastAPI REST endpoints integration testing.

---

## 🌟 Key Features & Functional Modules

### 1. 💬 कृषि मित्र चैट (Conversational Assistant)
- **Hindi-First Interaction**: Natural communication in Devanagari Hindi and Hinglish.
- **Voice In & Voice Out**: Integrated Web Speech API microphone input and Text-To-Speech (TTS) audio narration.
- **Transparent Agent Reasoning**: Displays real-time thought steps showing farmer profile retrieval, weather checks, tool execution, and safety validations.
- **Engagement Chips**: Clickable follow-up prompt suggestions that guide the farmer naturally.

### 2. 📸 फसल रोग जांच (Crop Disease Detection)
- Upload leaf photos to detect diseases across Tomato, Potato, Wheat, Rice, Cotton, Maize, Onion, and Grapes.
- Provides visual symptoms, causal pathogens, cultural methods, biological IPM solutions, and safe chemical treatments with precise dilution ratios.
- **Weather Spray Alert**: Automatically warns against spraying if rain is forecast within 24–48 hours.

### 3. 🧪 मृदा स्वास्थ्य कार्ड (Soil Health Analysis & Lab Locator)
- Accepts pH, EC, Organic Carbon, N, P, K, and micronutrients.
- Computes overall Soil Health Score (out of 100) and identifies specific deficiencies.
- Recommends corrective amendments (चूना for acidic soil, जिप्सम for alkaline soil, हरी खाद/जीवामृत for low organic carbon).
- Provides a directory of nearby Government Soil Testing Labs and KVKs with address, phone, and fee details.

### 4. 🌱 फसल चयन सलाहकार (Crop Recommendation Engine)
- Trained on 2,200+ samples covering 22 major Indian crops.
- Evaluates N, P, K, soil pH, rainfall, temperature, and humidity.
- One-click button to sync temperature and humidity directly from the live weather service!

### 5. 🌦️ मौसम व कृषि अलर्ट (Weather Intelligence)
- Real-time weather and 5-day forecasts for any district or GPS coordinates in India.
- Dynamic alerts for spray timing, irrigation scheduling, fungal disease risks, and frost mitigation.

### 6. 🏛️ सरकारी योजनाएं (Government Schemes Portal)
- Comprehensive catalog of farmer welfare schemes: PM-KISAN, PMFBY (फसल बीमा), Kisan Credit Card (KCC), Soil Health Card, PM-KUSUM (सोलर पंप).
- Complete details on eligibility, benefits, application processes, and toll-free helpline numbers.

### 7. 👤 किसान प्रोफाइल (Farmer Profile Persistence)
- Persistent SQLite storage remembering farmer name, village, district, state, land acreage, and primary crops for personalized recommendations.
