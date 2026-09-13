import io
from fastapi import APIRouter, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.core.orchestrator import agent_orchestrator
from app.core.memory import get_farmer_profile, update_farmer_profile
from app.modules.disease.detector import disease_detector
from app.modules.crop_recommender.model import crop_recommender
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.soil.parser import parse_soil_text_or_pdf
from app.modules.weather.service import get_weather_data, resolve_location
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories
from app.modules.schemes.scheme_catalog import scheme_catalog

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"
    farmer_id: Optional[str] = "default_farmer"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lang: Optional[str] = None

class CropRequest(BaseModel):
    n: float = 80.0
    p: float = 40.0
    k: float = 40.0
    temperature: float = 25.0
    humidity: float = 65.0
    ph: float = 6.8
    rainfall: float = 120.0
    month: int = 7

class SoilRequest(BaseModel):
    ph: float = 7.2
    ec: float = 0.4
    oc: float = 0.55
    n: float = 240.0
    p: float = 14.0
    k: float = 160.0
    zn: float = 0.8
    fe: float = 5.2
    s: float = 12.0
    state: str = "Uttar Pradesh"
    district: str = "Lucknow"

class ProfileRequest(BaseModel):
    farmer_id: str = "default_farmer"
    name: str = "रामसिंह वर्मा"
    village: str = "बख्शी का तालाब"
    district: str = "Lucknow"
    state: str = "Uttar Pradesh"
    farm_size_acres: float = 3.5
    current_crop: str = "गेहूं"
    soil_type: str = "जलोढ़ दोमट"
    irrigation_type: str = "ट्यूबवेल"
    language: str = "Hindi"

@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    return agent_orchestrator.process_query(
        query=req.message,
        session_id=req.session_id,
        farmer_id=req.farmer_id,
        latitude=req.latitude,
        longitude=req.longitude,
        lang=req.lang
    )

@router.post("/disease/detect")
async def detect_disease_endpoint(
    file: UploadFile = File(...),
    crop_hint: str = Form(""),
    rain_forecast: bool = Form(False),
    lang: str = Form("hi")
):
    contents = await file.read()
    return disease_detector.detect(contents, crop_hint=crop_hint, rain_forecast=rain_forecast, lang=lang)

@router.post("/soil/analyze")
def analyze_soil_endpoint(req: SoilRequest):
    analysis = analyze_soil_metrics(
        ph=req.ph, ec=req.ec, oc=req.oc,
        n=req.n, p=req.p, k=req.k,
        zn=req.zn, fe=req.fe, s=req.s,
        state=req.state
    )
    labs = find_nearby_soil_labs(state=req.state, district=req.district)
    analysis["nearby_labs"] = labs
    return analysis

@router.post("/soil/upload-card")
async def upload_soil_card_endpoint(
    file: UploadFile = File(...),
    state: str = Form("Uttar Pradesh"),
    district: str = Form("Lucknow")
):
    contents = await file.read()
    parsed_vals = parse_soil_text_or_pdf(file_bytes=contents)
    analysis = analyze_soil_metrics(
        ph=parsed_vals.get("ph", 7.2),
        ec=parsed_vals.get("ec", 0.45),
        oc=parsed_vals.get("oc", 0.52),
        n=parsed_vals.get("n", 235.0),
        p=parsed_vals.get("p", 12.5),
        k=parsed_vals.get("k", 175.0),
        state=state
    )
    analysis["extracted_parameters"] = parsed_vals
    analysis["nearby_labs"] = find_nearby_soil_labs(state=state, district=district)
    return analysis

@router.post("/crop/recommend")
def recommend_crop_endpoint(req: CropRequest):
    return crop_recommender.recommend(
        n=req.n, p=req.p, k=req.k,
        temperature=req.temperature,
        humidity=req.humidity,
        ph=req.ph,
        rainfall=req.rainfall,
        month=req.month
    )

@router.get("/weather")
def weather_endpoint(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    district: Optional[str] = None
):
    resolved_lat, resolved_lon, loc_label = resolve_location(district, lat, lon)
    weather_data = get_weather_data(resolved_lat, resolved_lon, loc_label)
    advisories = generate_agricultural_weather_advisories(weather_data)
    weather_data["agricultural_advisories"] = advisories
    return weather_data

@router.get("/schemes")
def schemes_endpoint(q: str = ""):
    return {"schemes": scheme_catalog.search(q)}

@router.get("/profile")
def get_profile_endpoint(farmer_id: str = "default_farmer"):
    return get_farmer_profile(farmer_id)

@router.post("/profile")
def update_profile_endpoint(req: ProfileRequest):
    update_farmer_profile(req.model_dump())
    return {"success": True, "message": "Profile updated successfully / प्रोफाइल सफलतापूर्वक अपडेट हुई।"}
