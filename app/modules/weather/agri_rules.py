from typing import Dict, Any, List, Optional

def generate_agricultural_weather_advisories(
    weather_data: Dict[str, Any],
    crop_context: Optional[str] = None,
    lang: str = "hi",
    **kwargs
) -> List[Dict[str, Any]]:

    """
    Evaluates meteorological parameters against deterministic agronomic thresholds.
    Generates actionable farm advisories for spraying, irrigation, and pathogen risks.
    """
    advisories = []
    curr = weather_data.get("current", {})
    forecast = weather_data.get("forecast", [])
    
    temp = curr.get("temperature", 28.0)
    humidity = curr.get("humidity", 65)
    wind_speed = curr.get("wind_speed", 8.0)
    rain_prob_today = forecast[0].get("rain_prob", 0) if forecast else 0
    rain_sum_today = forecast[0].get("rain_sum_mm", 0.0) if forecast else 0.0
    
    # 1. Chemical Spraying Window Advisory
    if rain_prob_today >= 35 or rain_sum_today > 2.0:
        advisories.append({
            "type": "warning",
            "code": "SPRAY_RAIN_RISK",
            "title": "⚠️ छिड़काव स्थगित चेतावनी (Rain Spray Alert)" if lang == "hi" else "⚠️ Spray Deferral Alert",
            "advice": (
                f"आज वर्षा की संभावना {rain_prob_today}% है। कीटनाशक या फफूंदनाशी का छिड़काव तुरंत टालें; "
                f"बारिश में दवा धुलकर नष्ट हो जाएगी और भूजल प्रदूषण का खतरा रहेगा।"
                if lang == "hi" else
                f"Rain probability is {rain_prob_today}%. Postpone all foliar pesticide and fungicide spraying "
                f"to prevent chemical wash-off and environmental contamination."
            )
        })
    elif wind_speed > 15.0:
        advisories.append({
            "type": "warning",
            "code": "HIGH_WIND_SPRAY_RISK",
            "title": "💨 तेज हवा अलर्ट (High Wind Spray Drift)" if lang == "hi" else "💨 High Wind Spray Alert",
            "advice": (
                f"हवा की गति {wind_speed} km/h अधिक है। तेज हवा में स्प्रे करने से दवा उड़कर पड़ोसी खेत "
                f"या आंखों में जा सकती है (ड्रिफ्ट रिस्क)। हवा शांत होने पर सुबह/शाम स्प्रे करें।"
                if lang == "hi" else
                f"Wind speed is {wind_speed} km/h. Avoid foliar spray during high winds to avoid spray drift "
                f"and uneven coverage. Spray early morning when air is still."
            )
        })
    else:
        advisories.append({
            "type": "optimal",
            "code": "SPRAY_WINDOW_FAVORABLE",
            "title": "✅ छिड़काव हेतु मौसम अनुकूल (Safe Spray Window)" if lang == "hi" else "✅ Favorable Spraying Window",
            "advice": (
                f"हवा धीमी ({wind_speed} km/h) और मौसम साफ है। आवश्यक कीटनाशक या सूक्ष्म पोषक तत्वों के "
                f"छिड़काव के लिए स्थिति उपयुक्त है।"
                if lang == "hi" else
                f"Wind speed ({wind_speed} km/h) is gentle and no immediate rain expected. Favorable conditions for foliar application."
            )
        })

    # 2. Fertilizer Application Timing
    heavy_rain_ahead = any(f.get("rain_prob", 0) >= 50 for f in forecast[:2])
    if heavy_rain_ahead:
        advisories.append({
            "type": "warning",
            "code": "FERTILIZER_LEACHING_RISK",
            "title": "🌧️ यूरिया/खाद उपयोग सलाह (Fertilizer Leaching Warning)" if lang == "hi" else "🌧️ Fertilizer Leaching Risk",
            "advice": (
                "अगले 48 घंटों में तेज बारिश की संभावना है। खड़ी फसल में यूरिया का टॉप-ड्रेसिंग न करें, "
                "अन्यथा नाइट्रोजन बहकर नष्ट हो जाएगी। बारिश रुकने और पानी उतरने के बाद ही खाद डालें।"
                if lang == "hi" else
                "Moderate to heavy rain forecast within 48 hours. Defer urea top-dressing to prevent leaching and surface runoff."
            )
        })

    # 3. Fungal Pathogen & Disease Climate Risk
    if humidity >= 80 and 18.0 <= temp <= 28.0:
        advisories.append({
            "type": "caution",
            "code": "HIGH_FUNGAL_RISK",
            "title": "🍄 फफूंद व झुलसा रोग अनुकूलता (Fungal Disease Alert)" if lang == "hi" else "🍄 Fungal Pathogen Risk",
            "advice": (
                f"वर्तमान उच्च आर्द्रता ({humidity}%) एवं तापमान ({temp}°C) झुलसा (Blight) एवं रतुआ (Rust) "
                f"जैसी फफूंद जनित बीमारियों के फैलने के लिए अनुकूल है। फसलों की पत्तियों का नियमित निरीक्षण करें।"
                if lang == "hi" else
                f"Elevated humidity ({humidity}%) and warm temperature ({temp}°C) favor fungal blights, rusts, and downy mildew. Monitor crop foliage closely."
            )
        })

    # 4. Cold Wave / Frost Risk
    min_temps = [f.get("temp_min", 20.0) for f in forecast[:3]]
    if min_temps and min(min_temps) <= 4.5:
        advisories.append({
            "type": "warning",
            "code": "FROST_COLD_WAVE_RISK",
            "title": "❄️ पाला एवं शीतलहर चेतावनी (Frost & Cold Wave Alert)" if lang == "hi" else "❄️ Frost & Cold Wave Alert",
            "advice": (
                f"रात का न्यूनतम तापमान गिरकर {min(min_temps)}°C तक जाने की आशंका है। आलू, सरसों व सब्जी की "
                f"फसलों को पाले से बचाने के लिए शाम को हल्की सिंचाई करें या खेत की मेड़ों पर धुआं करें।"
                if lang == "hi" else
                f"Overnight temperature dropping to {min(min_temps)}°C. Apply light irrigation or create perimeter smoke to protect potato and mustard from frost injury."
            )
        })

    for item in advisories:
        if "message" not in item:
            item["message"] = item.get("advice", "")

    return advisories

