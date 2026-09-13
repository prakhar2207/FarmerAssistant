import re
from typing import Dict, Any, List
from app.config import BANNED_CHEMICALS

DISCLAIMER_HINDI = "\n\n📌 *महत्वपूर्ण कृषि सूचना:* यह सलाह भारतीय कृषि अनुसंधान परिषद (ICAR) एवं वैज्ञानिक संस्तुतियों पर आधारित है। दवा का छिड़काव करते समय सुरक्षा किट (मास्क व दस्ताने) अवश्य पहनें। गंभीर स्थिति में तुरंत नजदीकी कृषि विज्ञान केंद्र (KVK) या किसान कॉल सेंटर 1800-180-1551 पर संपर्क करें।"

DISCLAIMER_ENGLISH = "\n\n📌 *Important Agricultural Notice:* This advisory is grounded in ICAR and government research package of practices. Always wear personal protective equipment (mask & gloves) during spraying. In critical infestations, contact your local Krishi Vigyan Kendra (KVK) or Kisan Call Centre: 1800-180-1551."

def validate_agricultural_safety(
    response_text: str,
    weather_rain_prob: float = 0.0,
    wind_speed: float = 0.0,
    lang: str = "hi"
) -> Dict[str, Any]:
    text_lower = response_text.lower()
    
    # 1. Screen against Banned Pesticides in India
    flagged_banned = []
    for chemical in BANNED_CHEMICALS:
        if chemical in text_lower:
            flagged_banned.append(chemical)

    cleaned_text = response_text
    safety_warnings = []
    
    if flagged_banned:
        for chemical in flagged_banned:
            replacement = f"[प्रतिबंधित रसायन: {chemical} - भारत सरकार द्वारा अमान्य]" if lang == "hi" else f"[Banned Chemical: {chemical} - Not Permitted by Govt of India]"
            cleaned_text = re.sub(re.escape(chemical), replacement, cleaned_text, flags=re.IGNORECASE)
            
        warning_msg = (
            f"⚠️ चेतावनी: {', '.join(flagged_banned)} भारत सरकार (CIBRC) द्वारा प्रतिबंधित रसायन है। इसके स्थान पर केवल संस्तुत सुरक्षित कीटनाशक का ही प्रयोग करें।"
            if lang == "hi"
            else f"⚠️ Warning: {', '.join(flagged_banned)} is a prohibited/banned agrochemical under CIBRC (Govt of India). Only use authorized safe formulations."
        )
        safety_warnings.append(warning_msg)

    # 2. Weather Spray Constraint
    if weather_rain_prob >= 30.0:
        warning_msg = (
            "⚠️ मौसम चेतावनी: आगामी 48 घंटों में बारिश की संभावना है। पर्ण छिड़काव (Foliar Spray) स्थगित रखें।"
            if lang == "hi"
            else "⚠️ Weather Alert: Rainfall anticipated within 48 hours. Postpone foliar spraying to prevent chemical wash-off."
        )
        safety_warnings.append(warning_msg)
    elif wind_speed > 15.0:
        warning_msg = (
            f"⚠️ हवा की गति ({wind_speed} किमी/घंटा) अधिक है, हवा के विपरीत दिशा में छिड़काव न करें।"
            if lang == "hi"
            else f"⚠️ High Wind Warning ({wind_speed} km/h): Do not spray against the wind direction to avoid drift hazards."
        )
        safety_warnings.append(warning_msg)

    final_text = cleaned_text
    if safety_warnings:
        final_text += "\n\n" + "\n".join(safety_warnings)
        
    final_text += (DISCLAIMER_HINDI if lang == "hi" else DISCLAIMER_ENGLISH)

    return {
        "safe_response": final_text,
        "is_safe": len(flagged_banned) == 0,
        "flagged_chemicals": flagged_banned,
        "safety_warnings": safety_warnings
    }
