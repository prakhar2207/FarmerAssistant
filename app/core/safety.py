import re
from typing import Dict, Any, List, Optional
from app.config import BANNED_CHEMICALS

DISCLAIMER_HINDI = "\n\n📌 *महत्वपूर्ण कृषि सूचना:* यह सलाह भारतीय कृषि अनुसंधान परिषद (ICAR) एवं वैज्ञानिक संस्तुतियों पर आधारित है। दवा का छिड़काव करते समय सुरक्षा किट (मास्क व दस्ताने) अवश्य पहनें। गंभीर स्थिति में तुरंत नजदीकी कृषि विज्ञान केंद्र (KVK) या किसान कॉल सेंटर 1800-180-1551 पर संपर्क करें।"

DISCLAIMER_ENGLISH = "\n\n📌 *Important Agricultural Notice:* This advisory is grounded in ICAR and government research package of practices. Always wear personal protective equipment (mask & gloves) during spraying. In critical infestations, contact your local Krishi Vigyan Kendra (KVK) or Kisan Call Centre: 1800-180-1551."

# Recommended CIBRC-Approved Safe Alternatives
SAFE_ALTERNATIVES = {
    "monocrotophos": {
        "reason_hi": "मोनोक्रोटोफॉस (Monocrotophos) अत्यधिक विषैला होने के कारण भारत सरकार (CIBRC) द्वारा सब्जियों एवं खाद्य फसलों पर पूर्णतः प्रतिबंधित है।",
        "reason_en": "Monocrotophos is strictly banned on vegetables and edible crops by the Govt of India (CIBRC) due to acute toxicity.",
        "alt_hi": "रस चूसक कीटों (माहू, सफेद मक्खी) के लिए सुरक्षित विकल्प: इमिडाक्लोप्रिड 17.8% एसएल (0.5 मिली/लीटर) या जैविक नीम तेल 1500 पीपीएम (3-4 मिली/लीटर) का छिड़काव करें।",
        "alt_en": "For sucking pests (aphids, whiteflies), safe approved alternatives: Imidacloprid 17.8% SL (0.5 ml/L) or organic Neem Oil 1500 ppm (3-4 ml/L)."
    },
    "endosulfan": {
        "reason_hi": "एंडोसल्फान (Endosulfan) सर्वोच्च न्यायालय एवं भारत सरकार द्वारा पर्यावरण व स्वास्थ्य खतरों के चलते पूर्ण रूप से प्रतिबंधित (Banned) है।",
        "reason_en": "Endosulfan is universally prohibited across India under Supreme Court order and CIBRC notification.",
        "alt_hi": "सुंडी व फल छेदक कीटों के लिए सुरक्षित विकल्प: कोराजन (क्लोरेंट्रानिलिप्रोल 18.5% एससी) 0.4 मिली/लीटर या इमामेक्टिन बेंजोएट 5% एसजी 0.5 ग्राम/लीटर प्रयोग करें।",
        "alt_en": "For caterpillars and fruit borers, safe approved alternatives: Chlorantraniliprole 18.5% SC (Coragen @ 0.4 ml/L) or Emamectin Benzoate 5% SG @ 0.5 g/L."
    },
    "phorate": {
        "reason_hi": "फोरेट (Phorate) अत्यधिक खतरनाक दानेदार कीटनाशक है और CIBRC द्वारा प्रतिबंधित/नियंत्रित है।",
        "reason_en": "Phorate is a banned/severely restricted chemical due to high soil and mammalian toxicity.",
        "alt_hi": "मृदा कीटों व दीमक हेतु सुरक्षित विकल्प: क्लोरपायरीफॉस या जैविक रूप से ब्यूवेरिया बासियाना (Beauveria bassiana) 2 किग्रा/एकड़ गोबर की खाद में मिलाकर डालें।",
        "alt_en": "For soil grubs and termites: Chlorpyrifos or biological Beauveria bassiana @ 2kg/acre blended with FYM."
    },
    "paraquat": {
        "reason_hi": "पैराक्वॉट डाइक्लोराइड (Paraquat Dichloride) अत्यधिक जानलेवा खरपतवारनाशी है और कई राज्यों में प्रतिबंधित है।",
        "reason_en": "Paraquat Dichloride is heavily restricted due to fatal toxicity without an antidote.",
        "alt_hi": "सुरक्षित विकल्प: ग्लाइफोसेट (गैर-फसल क्षेत्र) या फसल अनुरूप सुरक्षित चयनात्मक खरपतवारनाशी एवं यांत्रिक निराई-गुड़ाई अपनाएं।",
        "alt_en": "Safe alternatives: Recommended selective post-emergence herbicides matching the crop, or mechanical inter-cultivation weeding."
    }
}

def check_query_for_banned_chemicals(query: str, lang: str = "hi") -> Optional[Dict[str, Any]]:
    """Screens the farmer's question directly for prohibited agrochemicals."""
    q_lower = query.lower()
    for chemical in BANNED_CHEMICALS:
        if chemical in q_lower:
            alt_info = SAFE_ALTERNATIVES.get(chemical, {
                "reason_hi": f"{chemical.title()} भारत सरकार (CIBRC) द्वारा प्रतिबंधित रसायन है।",
                "reason_en": f"{chemical.title()} is a prohibited agrochemical under CIBRC, Government of India.",
                "alt_hi": "इसके स्थान पर केवल CIBRC द्वारा संस्तुत सुरक्षित जैविक या स्वीकृत रासायनिक कीटनाशक का प्रयोग करें।",
                "alt_en": "Please use authorized CIBRC approved bio-pesticides or non-hazardous crop protectants."
            })

            if lang == "en":
                response = (
                    f"🚫 **Safety Alert: Prohibited Agrochemical Detected!**\n\n"
                    f"• **Status:** {alt_info['reason_en']}\n"
                    f"• **Regulatory Authority:** Central Insecticides Board & Registration Committee (CIBRC)\n\n"
                    f"🌿 **Recommended Safe & Legal Alternatives:**\n"
                    f"• {alt_info['alt_en']}\n\n"
                    f"💡 Always prioritize Integrated Pest Management (IPM), pheromone traps, and biological controls."
                )
            else:
                response = (
                    f"🚫 **सुरक्षा चेतावनी: प्रतिबंधित कीटनाशक (Banned Chemical)**\n\n"
                    f"• **स्थिति:** {alt_info['reason_hi']}\n"
                    f"• **नियामक प्राधिकरण:** केंद्रीय कीटनाशक बोर्ड एवं पंजीकरण समिति (CIBRC, भारत सरकार)\n\n"
                    f"🌿 **अनुशंसित सुरक्षित एवं कानूनी विकल्प:**\n"
                    f"• {alt_info['alt_hi']}\n\n"
                    f"💡 रासायनिक दवाओं की जगह पहले एकीकृत कीट प्रबंधन (IPM), नीम का तेल व फेरोमोन ट्रैप अपनाएं।"
                )

            return {
                "is_banned": True,
                "chemical": chemical,
                "response": response + (DISCLAIMER_ENGLISH if lang == "en" else DISCLAIMER_HINDI),
                "safe_alternatives": alt_info
            }
    return None

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
            replacement = f"[प्रतिबंधित रसायन: {chemical} - CIBRC द्वारा अमान्य]" if lang == "hi" else f"[Prohibited Chemical: {chemical} - Not Permitted by CIBRC]"
            cleaned_text = re.sub(re.escape(chemical), replacement, cleaned_text, flags=re.IGNORECASE)
            
        warning_msg = (
            f"⚠️ चेतावनी: {', '.join(flagged_banned)} भारत सरकार (CIBRC) द्वारा प्रतिबंधित रसायन है। इसके स्थान पर सुरक्षित विकल्प ही प्रयोग करें।"
            if lang == "hi"
            else f"⚠️ Warning: {', '.join(flagged_banned)} is a prohibited agrochemical under CIBRC (Govt of India). Only use approved safe formulations."
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
