import re
from typing import Dict, Any, List, Optional

KNOWN_CROPS = {
    # Hindi
    "गेहूं": "wheat", "धान": "rice", "चावल": "rice", "मक्का": "maize",
    "आलू": "potato", "टमाटर": "tomato", "कपास": "cotton", "सरसों": "mustard",
    "चना": "chickpea", "प्याज": "onion", "अंगूर": "grapes", "गन्ना": "sugarcane",
    "केला": "banana", "आम": "mango", "तरबूज": "watermelon", "सोयाबीन": "soybean",
    "बाजरा": "pearl_millet", "ज्वार": "sorghum",
    # Hinglish
    "gehu": "wheat", "gehun": "wheat", "dhan": "rice", "chawal": "rice",
    "makka": "maize", "makai": "maize", "aloo": "potato", "aalu": "potato",
    "tamatar": "tomato", "kapas": "cotton", "sarson": "mustard", "sarso": "mustard",
    "chana": "chickpea", "pyaz": "onion", "pyaaz": "onion", "angur": "grapes",
    "angoor": "grapes", "ganna": "sugarcane", "kela": "banana", "aam": "mango",
    "tarbuj": "watermelon", "tarbooj": "watermelon", "soyabean": "soybean",
    "bajra": "pearl_millet", "jowar": "sorghum",
    # English
    "wheat": "wheat", "rice": "rice", "paddy": "rice", "maize": "maize", "corn": "maize",
    "potato": "potato", "tomato": "tomato", "cotton": "cotton", "mustard": "mustard",
    "chickpea": "chickpea", "gram": "chickpea", "onion": "onion", "grapes": "grapes",
    "grape": "grapes", "sugarcane": "sugarcane", "banana": "banana", "mango": "mango",
    "watermelon": "watermelon", "pulses": "pulses", "soybean": "soybean"
}

OUT_OF_DOMAIN_KEYWORDS = [
    "cricket", "match", "ipl", "score", "cinema", "movie", "film", "actor", "actress",
    "bollywood", "hollywood", "politics", "election", "vote", "modi", "rahul",
    "party", "bitcoin", "crypto", "stock market", "shares", "joke", "song", "dance",
    "cricketer", "football", "hockey", "tennis", "bcci",
    "क्रिकेट", "मैच", "सिनेमा", "फिल्म", "राजनीति", "चुनाव", "वोट", "शेयर", "मजाक", "गाना"
]

AGRI_KEYWORDS = [
    "फसल", "खेती", "किसान", "बीज", "खाद", "उर्वरक", "मिट्टी", "मृदा", "रोग", "कीट", "स्प्रे",
    "दवा", "छिड़काव", "सिंचाई", "मौसम", "योजना", "सब्सिडी", "पेड़", "पौधे", "पत्ती", "पत्तियां",
    "crop", "farm", "farming", "farmer", "seed", "fertilizer", "soil", "disease", "pest",
    "spray", "irrigation", "weather", "scheme", "subsidy", "plant", "leaf", "leaves",
    "fasal", "kheti", "kisan", "beej", "khad", "urvarak", "mitti", "rog", "keeda", "kida",
    "dawa", "dawaii", "chhidkaw", "sinchai", "mausam", "yojana", "patti", "pattiya"
]

def detect_language(text: str) -> str:
    """Detect if text is primarily Hindi (Devanagari) or English / Hinglish."""
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    latin_count = len(re.findall(r'[a-zA-Z]', text))
    return "hi" if devanagari_count >= latin_count else "en"

def detect_intent_and_slots(query: str, history: List[Dict[str, str]] = None, requested_lang: str = None) -> Dict[str, Any]:
    q = query.lower().strip()
    detected_lang = requested_lang if requested_lang in ["hi", "en"] else detect_language(query)
    
    # 0. Prompt Injection & Out of Domain Screening
    PROMPT_INJECTION_KEYWORDS = [
        "ignore previous", "ignore all previous", "act as a", "malicious hacker", "jailbreak",
        "system instructions", "system prompt", "bypass", "manufacture hazardous", "illegal poisons",
        "make explosives"
    ]
    if any(pik in q for pik in PROMPT_INJECTION_KEYWORDS):
        return {
            "intent": "OUT_OF_DOMAIN",
            "crop": None,
            "language": detected_lang,
            "missing_slots": [],
            "needs_clarification": False,
            "clarification_question": None,
            "confidence": 0.99
        }

    has_ood = any(ood in q for ood in OUT_OF_DOMAIN_KEYWORDS)
    if has_ood:
        return {
            "intent": "OUT_OF_DOMAIN",
            "crop": None,
            "language": detected_lang,
            "missing_slots": [],
            "needs_clarification": False,
            "clarification_question": None,
            "confidence": 0.98
        }


    # 1. Detect Crop Slot (with word boundary / token match)
    detected_crop = None
    # Check exact keywords or subwords
    for k_crop, en_crop in sorted(KNOWN_CROPS.items(), key=lambda x: -len(x[0])):
        pattern = r'\b' + re.escape(k_crop) + r'\b' if re.match(r'^[a-zA-Z0-9]+$', k_crop) else re.escape(k_crop)
        if re.search(pattern, q):
            detected_crop = en_crop
            break

    # Contextual carry-forward from conversation history
    if not detected_crop and history:
        for item in reversed(history):
            prev_msg = item.get("user_message", "").lower()
            for k_crop, en_crop in sorted(KNOWN_CROPS.items(), key=lambda x: -len(x[0])):
                pattern = r'\b' + re.escape(k_crop) + r'\b' if re.match(r'^[a-zA-Z0-9]+$', k_crop) else re.escape(k_crop)
                if re.search(pattern, prev_msg):
                    detected_crop = en_crop
                    break
            if detected_crop:
                break

    # 2. Intent Classification Keywords
    intent = "GENERAL_AGRI"
    confidence = 0.85
    
    disease_terms = [
        "रोग", "बीमारी", "धब्बा", "झुलसा", "रतुआ", "पीला", "पीले", "पीली", "सूख", "सड़न", "फफूंद", "सफेद चूर्ण", "खराब", "दवा", "दवाई", "उपचार", "रोकथाम", "इलाज",
        "disease", "spots", "spot", "blight", "rust", "yellow", "yellowing", "curl", "wilting", "rot", "mildew", "fungus",
        "peeli", "peela", "peele", "dhabba", "sukha", "sukhi", "jhulsa", "ratua", "safed churna", "kharab", "dawa", "dawai", "ilaj"
    ]
    pest_terms = [
        "कीड़ा", "कीट", "इल्ली", "माहू", "चेपा", "सुंडी", "मक्खी", "दीमक",
        "pest", "worm", "aphid", "aphids", "insect", "caterpillar", "borer", "whitefly", "armyworm", "termite",
        "keeda", "kida", "illi", "illii", "sundi", "mahu", "chepa", "makhi", "deemak"
    ]
    soil_terms = [
        "मिट्टी", "मृदा", "पीएच", "ph", "नाइट्रोजन", "फॉस्फोरस", "पोटाश", "कार्ड", "जांच", "लैब",
        "soil", "health card", "soil test", "soil analysis", "soil report", "organic carbon",
        "mitti", "mrida", "soil card", "mitti jaanch"
    ]
    fertilizer_terms = [
        "खाद", "उर्वरक", "यूरिया", "डीएपी", "dap", "urea", "पोटाश", "जीवामृत", "एनपीके", "npk",
        "fertilizer", "fertiliser", "manure", "dosage", "nutrition", "compost",
        "khad", "urvarak", "jeevamrut", "khad kitna", "dap kitna", "urea kitna"
    ]
    crop_rec_terms = [
        "कौन सी फसल", "क्या बोएं", "फसल चयन", "पैदावार", "फसल लगाएं", "फसल बोएं",
        "crop recommend", "suitable crop", "which crop", "what to grow", "best crop", "crop selection",
        "kaun si fasal", "kya boye", "fasal lagaye", "fasal lagana"
    ]
    weather_terms = [
        "मौसम", "बारिश", "तापमान", "हवा", "पाला", "कोहरा", "छिड़काव कर सकते", "स्प्रे कर सकते",
        "weather", "rain", "temperature", "forecast", "humidity", "rainfall", "frost", "can i spray",
        "mausam", "barish", "barsat", "tapman", "hawa", "pala", "kohra", "spray kar sakte"
    ]
    scheme_terms = [
        "योजना", "सब्सिडी", "सम्मान निधि", "बीमा", "kcc", "पंप", "कृषि यंत्र",
        "scheme", "subsidy", "pm kisan", "insurance", "pmfby", "credit card", "kusum", "yojana",
        "samman nidhi", "bima", "yantrikikaran"
    ]

    if any(term in q for term in weather_terms):
        intent = "WEATHER_FORECAST"
        confidence = 0.95
    elif any(term in q for term in scheme_terms):
        intent = "GOVT_SCHEME"
        confidence = 0.94
    elif any(term in q for term in disease_terms):
        intent = "DISEASE_DIAGNOSIS"
        confidence = 0.92
    elif any(term in q for term in pest_terms):
        intent = "PEST_CONTROL"
        confidence = 0.91
    elif any(term in q for term in soil_terms):
        intent = "SOIL_ANALYSIS"
        confidence = 0.93
    elif any(term in q for term in fertilizer_terms):
        intent = "FERTILIZER_ADVISORY"
        confidence = 0.92
    elif any(term in q for term in crop_rec_terms):
        intent = "CROP_RECOMMENDATION"
        confidence = 0.94

    # 3. Missing Slot & Clarification Detection
    missing_slots = []
    clarification_question = None
    
    if intent in ["DISEASE_DIAGNOSIS", "PEST_CONTROL"] and not detected_crop:
        missing_slots.append("crop")
        if detected_lang == "en":
            clarification_question = "Which crop (e.g. Wheat, Rice, Tomato, Potato) are you asking about, and on which plant part (leaves, stem, fruit) are the symptoms visible?"
        else:
            clarification_question = "आप किस फसल (जैसे गेहूं, धान, टमाटर, आलू आदि) के बारे में पूछ रहे हैं और पौधे के किस भाग (पत्ते, तने, फल) पर लक्षण दिखाई दे रहे हैं?"
    elif intent == "FERTILIZER_ADVISORY" and not detected_crop:
        missing_slots.append("crop")
        if detected_lang == "en":
            clarification_question = "Which crop are you requesting fertilizer recommendations for, and how old is the crop (in days/weeks)?"
        else:
            clarification_question = "आप किस फसल के लिए खाद की मात्रा जानना चाहते हैं और फसल कितने दिन की हो चुकी है?"
    elif intent == "SOIL_ANALYSIS" and not any(k in q for k in ["ph", "नाइट्रोजन", "रिपोर्ट", "कार्ड", "लैब", "test", "report", "lab", "jaanch"]):
        missing_slots.append("soil_data")
        if detected_lang == "en":
            clarification_question = "Do you have your Soil Health Card test values (pH, N, P, K) available, or would you like to find nearby government soil testing laboratories?"
        else:
            clarification_question = "क्या आपके पास मृदा स्वास्थ्य कार्ड (Soil Health Card) या मिट्टी जांच के आंकड़े (जैसे pH, N, P, K) उपलब्ध हैं, या आप नजदीकी सरकारी लैब का पता जानना चाहते हैं?"

    return {
        "intent": intent,
        "crop": detected_crop,
        "language": detected_lang,
        "missing_slots": missing_slots,
        "needs_clarification": bool(clarification_question),
        "clarification_question": clarification_question,
        "confidence": confidence
    }
