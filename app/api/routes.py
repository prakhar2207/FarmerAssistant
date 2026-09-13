import io
import logging
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.core.orchestrator import agent_orchestrator
from app.core.memory import (
    get_farmer_profile,
    update_farmer_profile,
    get_chat_sessions,
    get_session_turns,
    delete_chat_session,
    clear_all_chat_history
)
from app.modules.disease.detector import disease_detector
from app.modules.crop_recommender.model import crop_recommender
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.soil.parser import parse_soil_text_or_pdf
from app.modules.weather.service import get_weather_data, resolve_location
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories
from app.modules.schemes.scheme_catalog import scheme_catalog

logger = logging.getLogger("krishi_saathi.api")
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"
    farmer_id: Optional[str] = "default_farmer"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lang: Optional[str] = None

class CropRequest(BaseModel):
    n: float = Field(default=80.0, ge=0, le=500)
    p: float = Field(default=40.0, ge=0, le=300)
    k: float = Field(default=40.0, ge=0, le=400)
    temperature: float = Field(default=25.0, ge=-10, le=60)
    humidity: float = Field(default=65.0, ge=0, le=100)
    ph: float = Field(default=6.8, ge=2, le=14)
    rainfall: float = Field(default=120.0, ge=0, le=2000)
    month: int = Field(default=7, ge=1, le=12)

class SoilRequest(BaseModel):
    ph: float = Field(default=7.2, ge=2, le=14)
    ec: float = Field(default=0.4, ge=0)
    oc: float = Field(default=0.55, ge=0, le=10)
    n: float = Field(default=240.0, ge=0)
    p: float = Field(default=14.0, ge=0)
    k: float = Field(default=160.0, ge=0)
    zn: float = Field(default=0.8, ge=0)
    fe: float = Field(default=5.2, ge=0)
    s: float = Field(default=12.0, ge=0)
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


# ---------------------------------------------------------
# Chat & Multimodal Endpoints
# ---------------------------------------------------------
@router.post("/chat")
def chat_endpoint(req: ChatRequest):
    try:
        if not req.message or not req.message.strip():
            return {
                "response": "कृपया अपना कृषि प्रश्न लिखें या बोलें। / Please enter your farming question.",
                "intent": "GENERAL_AGRI",
                "language": req.lang or "hi",
                "status_badges": [],
                "thought_steps": [],
                "citations": [],
                "follow_up_suggestions": ["गेहूं में खाद की मात्रा", "धान की वैज्ञानिक खेती", "मौसम का पूर्वानुमान"]
            }

        res = agent_orchestrator.process_query(
            query=req.message,
            session_id=req.session_id or "default_session",
            farmer_id=req.farmer_id or "default_farmer",
            latitude=req.latitude,
            longitude=req.longitude,
            lang=req.lang
        )
        if isinstance(res, dict):
            res.setdefault("success", True)
        return res
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "response": "क्षमा करें, आपके अनुरोध को संसाधित करते समय समस्या आई। कृपया पुनः प्रयास करें। / An error occurred while processing your request. Please try again.",
            "intent": "ERROR",
            "language": req.lang or "hi",
            "status_badges": [],
            "thought_steps": [],
            "citations": [],
            "follow_up_suggestions": []
        }

@router.post("/chat/multimodal")
async def multimodal_chat_endpoint(
    message: str = Form(""),
    file: Optional[UploadFile] = File(None),
    session_id: str = Form("default_session"),
    farmer_id: str = Form("default_farmer"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    lang: Optional[str] = Form(None)
):
    try:
        image_bytes = None
        if file:
            image_bytes = await file.read()

        clean_message = message.strip() if message else ""
        if not clean_message and not image_bytes:
            clean_message = "नमस्ते / Hello"

        res = agent_orchestrator.process_query(
            query=clean_message,
            image_bytes=image_bytes,
            session_id=session_id or "default_session",
            farmer_id=farmer_id or "default_farmer",
            latitude=latitude,
            longitude=longitude,
            lang=lang
        )
        if isinstance(res, dict):
            res.setdefault("success", True)
        return res
    except Exception as e:
        logger.error(f"Error in multimodal_chat_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "response": "क्षमा करें, छवि या संदेश को प्रोसेस करने में त्रुटि हुई। कृपया साफ़ फोटो के साथ पुनः प्रयास करें।",
            "intent": "ERROR",
            "language": lang or "hi",
            "status_badges": [],
            "thought_steps": [],
            "citations": [],
            "follow_up_suggestions": []
        }

@router.get("/chat/sessions")
def get_sessions_endpoint(farmer_id: str = "default_farmer"):
    """Lists recent conversation sessions for the ChatGPT-like sidebar."""
    try:
        sessions = get_chat_sessions(farmer_id=farmer_id, limit=30)
        return {"success": True, "sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return {"success": False, "sessions": [], "error": str(e)}

@router.get("/chat/history/{session_id}")
def get_session_history_endpoint(session_id: str):
    """Fetches full conversation history for a selected session."""
    try:
        turns = get_session_turns(session_id=session_id)
        return {"success": True, "session_id": session_id, "messages": turns}
    except Exception as e:
        logger.error(f"Error getting history for {session_id}: {e}")
        return {"success": False, "session_id": session_id, "messages": [], "error": str(e)}

@router.delete("/chat/sessions/{session_id}")
def delete_session_endpoint(session_id: str):
    """Deletes a chat session."""
    try:
        delete_chat_session(session_id=session_id)
        return {"success": True, "message": f"Session {session_id} deleted."}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------
# Computer Vision Disease Diagnostic
# ---------------------------------------------------------
@router.post("/disease/detect")
async def detect_disease_endpoint(
    file: UploadFile = File(...),
    crop_hint: str = Form(""),
    rain_forecast: bool = Form(False),
    lang: str = Form("hi")
):
    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            return {
                "success": False,
                "error": "कृपया एक वैध छवि फ़ाइल अपलोड करें।" if lang == "hi" else "Please upload a valid image file."
            }
        return disease_detector.detect(contents, crop_hint=crop_hint, rain_forecast=rain_forecast, lang=lang)
    except Exception as e:
        logger.error(f"Error in detect_disease_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "error": "छवि प्रसंस्करण में त्रुटि। कृपया साफ़ फोटो पुनः अपलोड करें।" if lang == "hi" else "Image processing error. Please upload a clear photo again."
        }


# ---------------------------------------------------------
# Soil Intelligence & Laboratory Finder
# ---------------------------------------------------------
@router.post("/soil/analyze")
def analyze_soil_endpoint(req: SoilRequest):
    try:
        analysis = analyze_soil_metrics(
            ph=req.ph, ec=req.ec, oc=req.oc,
            n=req.n, p=req.p, k=req.k,
            zn=req.zn, fe=req.fe, s=req.s,
            state=req.state
        )
        labs = find_nearby_soil_labs(state=req.state, district=req.district)
        analysis["nearby_labs"] = labs
        analysis["success"] = True
        return analysis
    except Exception as e:
        logger.error(f"Error in analyze_soil_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "health_score": 50,
            "deficiencies": ["मृदा विश्लेषण में त्रुटि। कृपया मान जांचें।"],
            "deficiencies_en": ["Soil analysis error. Please verify input metrics."],
            "amendments": [],
            "nearby_labs": []
        }

@router.post("/soil/upload-card")
async def upload_soil_card_endpoint(
    file: UploadFile = File(...),
    state: str = Form("Uttar Pradesh"),
    district: str = Form("Lucknow")
):
    try:
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
        analysis["success"] = True
        return analysis
    except Exception as e:
        logger.error(f"Error in upload_soil_card_endpoint: {e}", exc_info=True)
        return {"success": False, "error": "मृदा कार्ड पढ़ने में त्रुटि।"}


# ---------------------------------------------------------
# Crop Recommendation Engine
# ---------------------------------------------------------
@router.post("/crop/recommend")
def recommend_crop_endpoint(req: CropRequest):
    try:
        return crop_recommender.recommend(
            n=req.n, p=req.p, k=req.k,
            temperature=req.temperature,
            humidity=req.humidity,
            ph=req.ph,
            rainfall=req.rainfall,
            month=req.month
        )
    except Exception as e:
        logger.error(f"Error in recommend_crop_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "top_recommendations": [],
            "summary_hindi": "फसल अनुशंसा की गणना में त्रुटि।",
            "summary_english": "Error calculating crop recommendation."
        }


# ---------------------------------------------------------
# Weather Intelligence & Agro-Rules
# ---------------------------------------------------------
@router.get("/weather")
def weather_endpoint(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    district: Optional[str] = None
):
    try:
        resolved_lat, resolved_lon, loc_label = resolve_location(district, lat, lon)
        weather_data = get_weather_data(resolved_lat, resolved_lon, loc_label)
        advisories = generate_agricultural_weather_advisories(weather_data)
        weather_data["agricultural_advisories"] = advisories
        return weather_data
    except Exception as e:
        logger.error(f"Error in weather_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "location": district or "India",
            "current": {"temperature": 28.0, "humidity": 65, "wind_speed": 8.0, "condition": "Clear"},
            "forecast": [],
            "agricultural_advisories": []
        }


# ---------------------------------------------------------
# Government Schemes Catalog
# ---------------------------------------------------------
@router.get("/schemes")
def schemes_endpoint(q: str = ""):
    try:
        return {"success": True, "schemes": scheme_catalog.search(q)}
    except Exception as e:
        logger.error(f"Error in schemes_endpoint: {e}", exc_info=True)
        return {"success": False, "schemes": []}


# ---------------------------------------------------------
# Farmer Profile & Memory
# ---------------------------------------------------------
@router.get("/profile")
def get_profile_endpoint(farmer_id: str = "default_farmer"):
    try:
        return get_farmer_profile(farmer_id)
    except Exception as e:
        logger.error(f"Error in get_profile_endpoint: {e}", exc_info=True)
        return {"farmer_id": farmer_id, "name": "किसान", "district": "Lucknow", "state": "Uttar Pradesh"}

@router.post("/profile")
def update_profile_endpoint(req: ProfileRequest):
    try:
        update_farmer_profile(req.model_dump())
        return {"success": True, "message": "Profile updated successfully / प्रोफाइल सफलतापूर्वक अपडेट हुई।"}
    except Exception as e:
        logger.error(f"Error in update_profile_endpoint: {e}", exc_info=True)
        return {"success": False, "message": "प्रोफाइल अपडेट करने में त्रुटि।"}
