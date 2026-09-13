import re
from typing import Dict, Any, List

# Indian agricultural crops keywords in Hindi & English
KNOWN_CROPS = {
    "गेहूं": "wheat", "wheat": "wheat",
    "धान": "rice", "चावल": "rice", "rice": "rice", "paddy": "rice",
    "मक्का": "maize", "maize": "maize", "corn": "maize",
    "आलू": "potato", "potato": "potato",
    "टमाटर": "tomato", "tomato": "tomato",
    "कपास": "cotton", "cotton": "cotton",
    "सरसों": "mustard", "mustard": "mustard",
    "चना": "chickpea", "chickpea": "chickpea",
    "प्याज": "onion", "onion": "onion",
    "अंगूर": "grapes", "grapes": "grapes",
    "गन्ना": "sugarcane", "sugarcane": "sugarcane"
}

def detect_intent_and_slots(query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    q = query.lower()
    
    # 1. Detect Crop Slot
    detected_crop = None
    for k_crop, en_crop in KNOWN_CROPS.items():
        if k_crop in q:
            detected_crop = en_crop
            break
            
    # If not in current query, check previous history
    if not detected_crop and history:
        for item in reversed(history):
            prev_msg = item.get("user_message", "").lower()
            for k_crop, en_crop in KNOWN_CROPS.items():
                if k_crop in prev_msg:
                    detected_crop = en_crop
                    break
            if detected_crop:
                break

    # 2. Intent Classification
    intent = "GENERAL_AGRI"
    
    if any(term in q for term in ["रोग", "बीमारी", "धब्बा", "झुलसा", "रतुआ", "पीला", "पीले", "सूख", "सड़न", "फफूंद", "सफेद चूर्ण", "disease", "spots", "curl", "yellow"]):
        intent = "DISEASE_DIAGNOSIS"
    elif any(term in q for term in ["कीड़ा", "कीट", "इल्ली", "माहू", "चेपा", "सुंडी", "मक्खी", "pest", "worm", "aphid"]):
        intent = "PEST_CONTROL"
    elif any(term in q for term in ["मिट्टी", "मृदा", "पीएच", "ph", "नाइट्रोजन", "फॉस्फोरस", "पोटाश", "soil", "health card", "जांच"]):
        intent = "SOIL_ANALYSIS"
    elif any(term in q for term in ["खाद", "उर्वरक", "यूरिया", "डीएपी", "dap", "urea", "पोटाश", "जीवामृत", "fertilizer"]):
        intent = "FERTILIZER_ADVISORY"
    elif any(term in q for term in ["कौन सी फसल", "क्या बोएं", "फसल चयन", "पैदावार", "crop recommend", "suitable crop"]):
        intent = "CROP_RECOMMENDATION"
    elif any(term in q for term in ["मौसम", "बारिश", "तापमान", "हवा", "पाला", "कोहरा", "weather", "rain", "forecast"]):
        intent = "WEATHER_FORECAST"
    elif any(term in q for term in ["योजना", "सब्सिडी", "सम्मान निधि", "बीमा", "kcc", "पंप", "scheme", "subsidy", "pm kisan"]):
        intent = "GOVT_SCHEME"

    # 3. Missing Slot & Clarification Detection (Krishi Sathi approach)
    missing_slots = []
    clarification_question = None
    
    if intent in ["DISEASE_DIAGNOSIS", "PEST_CONTROL"] and not detected_crop:
        missing_slots.append("crop")
        clarification_question = "आप किस फसल (जैसे गेहूं, धान, टमाटर, आलू आदि) के बारे में पूछ रहे हैं और पौधे के किस भाग (पत्ते, तने, फल) पर लक्षण दिखाई दे रहे हैं?"
    elif intent == "FERTILIZER_ADVISORY" and not detected_crop:
        missing_slots.append("crop")
        clarification_question = "आप किस फसल के लिए खाद की मात्रा जानना चाहते हैं और फसल कितने दिन की हो चुकी है?"
    elif intent == "SOIL_ANALYSIS" and not any(k in q for k in ["ph", "नाइट्रोजन", "रिपोर्ट", "कार्ड", "लैब"]):
        missing_slots.append("soil_data")
        clarification_question = "क्या आपके पास मृदा स्वास्थ्य कार्ड (Soil Health Card) या मिट्टी जांच के आंकड़े (जैसे pH, N, P, K) उपलब्ध हैं, या आप नजदीकी सरकारी लैब का पता जानना चाहते हैं?"

    return {
        "intent": intent,
        "crop": detected_crop,
        "missing_slots": missing_slots,
        "needs_clarification": bool(clarification_question),
        "clarification_question": clarification_question
    }
