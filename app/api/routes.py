import json
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.core.orchestrator import agent_orchestrator
from app.core.security import validate_and_save_upload
from app.core.memory import (
    get_farmer_profile,
    update_farmer_profile,
    get_chat_sessions,
    get_session_turns,
    delete_chat_session
)
from app.modules.disease.yolo_service import yolo_leaf_service
from app.modules.crop_recommender.model import crop_recommender
from app.modules.fertilizer.calculator import calculate_fertilizer_schedule
from app.modules.pest.advisory import get_pest_advisory
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.soil.parser import parse_soil_text_or_pdf
from app.modules.weather.service import get_weather_data, resolve_location
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories
from app.modules.schemes.scheme_catalog import scheme_catalog

logger = logging.getLogger("krishi_saathi.api")
router = APIRouter()

# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"
    farmer_id: Optional[str] = "default_farmer"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    lang: Optional[str] = None

class CropRequest(BaseModel):
    soil_type: Optional[str] = "alluvial"
    temperature: float = Field(default=26.0, ge=-10, le=60)
    humidity: float = Field(default=65.0, ge=0, le=100)
    rainfall_mm: float = Field(default=120.0, ge=0, le=3000)
    rainfall: Optional[float] = None
    month: Optional[int] = None
    season: Optional[str] = "rabi"
    n: Optional[float] = 80.0
    p: Optional[float] = 40.0
    k: Optional[float] = 40.0
    ph: Optional[float] = 7.0

class SoilRequest(BaseModel):
    ph: Optional[float] = Field(default=7.2, ge=2, le=14)
    ec: Optional[float] = Field(default=0.4, ge=0)
    oc: Optional[float] = Field(default=0.55, ge=0, le=10)
    n: Optional[float] = Field(default=240.0, ge=0)
    p: Optional[float] = Field(default=14.0, ge=0)
    k: Optional[float] = Field(default=160.0, ge=0)
    zn: Optional[float] = Field(default=0.8, ge=0)
    fe: Optional[float] = Field(default=5.2, ge=0)
    s: Optional[float] = Field(default=12.0, ge=0)
    crop_key: Optional[str] = "wheat"
    state: Optional[str] = "Uttar Pradesh"
    district: Optional[str] = "Lucknow"

class FertilizerRequest(BaseModel):
    crop: str = "wheat"
    acres: float = Field(default=1.0, gt=0, le=1000)
    soil_n: Optional[float] = 220.0
    soil_p: Optional[float] = 12.0
    soil_k: Optional[float] = 150.0
    rain_forecast_48h: Optional[bool] = False

class PestRequest(BaseModel):
    query: str
    crop: Optional[str] = ""

class ProfileRequest(BaseModel):
    farmer_id: str = "default_farmer"
    name: str = "रामसिंह वर्मा"
    village: Optional[str] = "बख्शी का तालाब"
    district: str = "Lucknow"
    state: str = "Uttar Pradesh"
    land_acres: Optional[float] = 3.5
    current_crop: Optional[str] = "गेहूं"
    soil_type: Optional[str] = "alluvial"
    irrigation_type: Optional[str] = "tubewell"
    language: Optional[str] = "Hindi"

# ---------------------------------------------------------
# Chat & Conversational Stream Endpoints
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
            "response": "क्षमा करें, आपके अनुरोध को संसाधित करते समय समस्या आई। कृपया पुनः प्रयास करें।",
            "intent": "ERROR",
            "language": req.lang or "hi",
            "status_badges": [],
            "thought_steps": [],
            "citations": [],
            "follow_up_suggestions": []
        }

@router.post("/chat/stream")
def chat_stream_endpoint(req: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint providing real-time status badges,
    reasoning thoughts, and incremental text chunks to the frontend.
    """
    def event_generator():
        try:
            for event in agent_orchestrator.process_query_stream(
                query=req.message,
                session_id=req.session_id or "default_session",
                farmer_id=req.farmer_id or "default_farmer",
                latitude=req.latitude,
                longitude=req.longitude,
                lang=req.lang
            ):
                payload = json.dumps(event, ensure_ascii=False)
                yield f"data: {payload}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            err_payload = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
            _, image_bytes = await validate_and_save_upload(file, allowed_types=('image/',))

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
    except HTTPException as he:
        return {"success": False, "response": he.detail, "intent": "SECURITY_ERROR"}
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
    try:
        sessions = get_chat_sessions(farmer_id=farmer_id, limit=30)
        return {"success": True, "sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return {"success": False, "sessions": [], "error": str(e)}

@router.get("/chat/history/{session_id}")
def get_session_history_endpoint(session_id: str):
    try:
        turns = get_session_turns(session_id=session_id)
        return {"success": True, "session_id": session_id, "messages": turns}
    except Exception as e:
        logger.error(f"Error getting history for {session_id}: {e}")
        return {"success": False, "session_id": session_id, "messages": [], "error": str(e)}

@router.delete("/chat/sessions/{session_id}")
def delete_session_endpoint(session_id: str):
    try:
        delete_chat_session(session_id=session_id)
        return {"success": True, "message": f"Session {session_id} deleted."}
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return {"success": False, "error": str(e)}

# ---------------------------------------------------------
# Foliar Disease Computer Vision Diagnostic
# ---------------------------------------------------------
@router.post("/disease/detect")
@router.post("/disease/analyze")
async def detect_disease_endpoint(
    file: UploadFile = File(...),
    crop_hint: str = Form(""),
    rain_forecast: bool = Form(False),
    lang: str = Form("hi")
):
    try:
        _, contents = await validate_and_save_upload(file, allowed_types=('image/',))
        return yolo_leaf_service.infer(
            image_bytes=contents,
            crop_hint=crop_hint,
            rain_forecast=rain_forecast,
            lang=lang
        )
    except HTTPException as he:
        return {"success": False, "is_leaf": False, "rejection_reason": he.detail}
    except Exception as e:
        logger.error(f"Error in detect_disease_endpoint: {e}", exc_info=True)
        return {
            "success": False,
            "is_leaf": False,
            "rejection_reason": "छवि प्रसंस्करण में त्रुटि। कृपया साफ़ फोटो पुनः अपलोड करें।" if lang == "hi" else "Image processing error. Please upload a clear leaf photo."
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
            crop_key=req.crop_key or "wheat"
        )
        labs = find_nearby_soil_labs(district=req.district or "Lucknow", state=req.state or "Uttar Pradesh")
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
    district: str = Form("Lucknow"),
    crop_key: str = Form("wheat")
):
    try:
        _, contents = await validate_and_save_upload(file, allowed_types=('image/', 'application/pdf'))
        parsed = parse_soil_text_or_pdf(file_bytes=contents)
        params = parsed.get("extracted_parameters", {})
        analysis = analyze_soil_metrics(
            ph=params.get("ph"),
            ec=params.get("ec"),
            oc=params.get("oc"),
            n=params.get("n"),
            p=params.get("p"),
            k=params.get("k"),
            zn=params.get("zn"),
            fe=params.get("fe"),
            s=params.get("s"),
            crop_key=crop_key
        )
        analysis["parsed_card"] = parsed
        analysis["nearby_labs"] = find_nearby_soil_labs(district=district, state=state)
        analysis["success"] = True
        return analysis
    except HTTPException as he:
        return {"success": False, "error": he.detail}
    except Exception as e:
        logger.error(f"Error in upload_soil_card_endpoint: {e}", exc_info=True)
        return {"success": False, "error": f"मृदा कार्ड पढ़ने में त्रुटि: {str(e)}"}

# ---------------------------------------------------------
# Crop & Fertilizer Recommendation
# ---------------------------------------------------------
@router.post("/crop/recommend")
def recommend_crop_endpoint(req: CropRequest):
    try:
        eff_rainfall = req.rainfall if req.rainfall is not None else req.rainfall_mm
        recs = crop_recommender.recommend(
            soil_type=req.soil_type or "alluvial",
            temperature=req.temperature,
            humidity=req.humidity,
            rainfall_mm=eff_rainfall,
            season=req.season or "rabi",
            n=req.n,
            p=req.p,
            k=req.k,
            ph=req.ph,
            rainfall=eff_rainfall,
            month=req.month,
            top_k=3
        )
        rec_list = recs.get("top_recommendations", recs) if isinstance(recs, dict) else recs
        return {
            "success": True,
            "recommendations": rec_list,
            "top_recommendations": rec_list,
            "total_matches": len(rec_list)
        }
    except Exception as e:
        logger.error(f"Error in recommend_crop_endpoint: {e}", exc_info=True)
        return {"success": False, "recommendations": [], "top_recommendations": [], "error": str(e)}

@router.post("/fertilizer/recommend")
def recommend_fertilizer_endpoint(req: FertilizerRequest):
    try:
        sched = calculate_fertilizer_schedule(
            crop=req.crop,
            soil_n=req.soil_n or 220.0,
            soil_p=req.soil_p or 12.0,
            soil_k=req.soil_k or 150.0,
            rain_forecast_48h=bool(req.rain_forecast_48h),
            acres=req.acres
        )
        sched["success"] = True
        return sched
    except Exception as e:
        logger.error(f"Error in fertilizer endpoint: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@router.post("/pest/analyze")
def analyze_pest_endpoint(req: PestRequest):
    try:
        advisory = get_pest_advisory(pest_or_symptom=req.query, crop=req.crop or "")
        advisory["success"] = True
        return advisory
    except Exception as e:
        logger.error(f"Error in pest endpoint: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

# ---------------------------------------------------------
# Weather Intelligence & Agro-Rules
# ---------------------------------------------------------
@router.get("/weather")
@router.get("/weather/current")
@router.get("/weather/forecast")
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
        weather_data["success"] = True
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

@router.get("/location/resolve")
def resolve_location_endpoint(district: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None):
    try:
        rlat, rlon, rloc = resolve_location(district, lat, lon)
        return {"success": True, "latitude": rlat, "longitude": rlon, "label": rloc}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------------------------------------------------------
# Government Schemes Catalog
# ---------------------------------------------------------
@router.get("/schemes")
def schemes_endpoint(
    q: str = "",
    state: Optional[str] = None,
    land_acres: Optional[float] = None
):
    try:
        if state or land_acres is not None:
            results = scheme_catalog.find_eligible_schemes(state=state, land_acres=land_acres)
        else:
            results = scheme_catalog.search(q)
        return {"success": True, "schemes": results}
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
@router.put("/profile")
def update_profile_endpoint(req: ProfileRequest):
    try:
        update_farmer_profile(req.model_dump())
        return {"success": True, "message": "Profile updated successfully / प्रोफाइल सफलतापूर्वक अपडेट हुई।"}
    except Exception as e:
        logger.error(f"Error in update_profile_endpoint: {e}", exc_info=True)
        return {"success": False, "message": "प्रोफाइल अपडेट करने में त्रुटि।"}
