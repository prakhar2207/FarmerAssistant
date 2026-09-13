from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from app.core.agent_state import AgentState

@dataclass
class AgroContext:
    """
    Unified, structured agronomic and environmental context.
    Prepares extracted facts, temporal day weather, and soil status for response planning.
    """
    query: str
    intent: str
    crop: Optional[str]
    target_day: str  # today, tomorrow, day_after, forecast
    action_type: Optional[str]  # spray, fertilizer, irrigation, sowing, harvest
    location_label: str
    language: str
    farmer_profile: Dict[str, Any]
    
    # Weather metrics
    current_temp: float
    current_humidity: int
    current_wind_speed: float
    target_rain_prob: int
    target_rain_mm: float
    target_condition_hi: str
    target_condition_en: str
    target_temp_max: float
    target_temp_min: float
    rain_expected_48h: bool
    weather_raw: Dict[str, Any]

    # Soil metrics
    soil_data: Optional[Dict[str, Any]]
    soil_type: str

    # Vision & history
    vision_result: Optional[Dict[str, Any]]
    chat_history: List[Dict[str, Any]]

def build_agro_context(state: AgentState) -> AgroContext:
    """
    Extracts and organizes meteorological, agronomic, and profile facts from AgentState.
    """
    weather = state.weather or {}
    forecast = weather.get("forecast", [])
    current = weather.get("current", {})

    target_rain_prob = state.rain_prob
    target_rain_mm = 0.0
    target_condition_hi = current.get("condition", "साफ मौसम")
    target_condition_en = current.get("condition_en", "Clear")
    target_temp_max = current.get("temperature", state.temp)
    target_temp_min = current.get("temperature", state.temp) - 8.0

    # Resolve target day weather from forecast array
    if state.target_day == "tomorrow" and len(forecast) > 1:
        f_day = forecast[1]
        target_rain_prob = f_day.get("rain_prob", target_rain_prob)
        target_rain_mm = f_day.get("rain_sum_mm", 0.0)
        target_condition_hi = f_day.get("condition", target_condition_hi)
        target_condition_en = f_day.get("condition_en", target_condition_en)
        target_temp_max = f_day.get("temp_max", target_temp_max)
        target_temp_min = f_day.get("temp_min", target_temp_min)
    elif state.target_day == "day_after" and len(forecast) > 2:
        f_day = forecast[2]
        target_rain_prob = f_day.get("rain_prob", target_rain_prob)
        target_rain_mm = f_day.get("rain_sum_mm", 0.0)
        target_condition_hi = f_day.get("condition", target_condition_hi)
        target_condition_en = f_day.get("condition_en", target_condition_en)
        target_temp_max = f_day.get("temp_max", target_temp_max)
        target_temp_min = f_day.get("temp_min", target_temp_min)
    elif len(forecast) > 0:
        f_day = forecast[0]
        target_rain_prob = f_day.get("rain_prob", target_rain_prob)
        target_rain_mm = f_day.get("rain_sum_mm", current.get("precipitation", 0.0))
        target_condition_hi = f_day.get("condition", target_condition_hi)
        target_condition_en = f_day.get("condition_en", target_condition_en)
        target_temp_max = f_day.get("temp_max", target_temp_max)
        target_temp_min = f_day.get("temp_min", target_temp_min)

    soil_type = state.farmer_profile.get("soil_type", "दोमट (Alluvial)")

    return AgroContext(
        query=state.raw_query,
        intent=str(state.intent),
        crop=state.crop,
        target_day=state.target_day,
        action_type=state.action_type,
        location_label=state.location_label,
        language=state.detected_language,
        farmer_profile=state.farmer_profile,
        current_temp=state.temp,
        current_humidity=state.humidity,
        current_wind_speed=state.wind_speed,
        target_rain_prob=target_rain_prob,
        target_rain_mm=target_rain_mm,
        target_condition_hi=target_condition_hi,
        target_condition_en=target_condition_en,
        target_temp_max=target_temp_max,
        target_temp_min=target_temp_min,
        rain_expected_48h=state.rain_expected_48h,
        weather_raw=weather,
        soil_data=state.soil_data,
        soil_type=soil_type,
        vision_result=state.vision_result,
        chat_history=state.chat_history
    )
