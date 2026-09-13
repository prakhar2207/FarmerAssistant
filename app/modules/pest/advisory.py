from typing import Dict, Any, List

PEST_CATALOG = {
    "aphids": {
        "name_hindi": "माहू / चेपा (Aphids)",
        "crops": ["सरसों", "गेहूं", "सब्जियां", "दलहन"],
        "symptoms": "छोटे पीले, हरे या काले कीड़े पत्तियों व तनों से रस चूसते हैं। पत्तियां मुड़ जाती हैं और चिपचिपा तरल निकलता है जिस पर काली फफूंद जमती है।",
        "ipm_cultural": [
            "पीले चिपचिपे ट्रैप (Yellow Sticky Traps) 15-20 प्रति एकड़ लगाएं।",
            "खेत में मित्र कीट जैसे लेडीबर्ड बीटल (लेडीबग) का संरक्षण करें।"
        ],
        "biological": [
            "नीम का तेल (Neem Oil 10,000 ppm) 3 मिली प्रति लीटर पानी में शैम्पू के साथ घोलकर छिड़कें।",
            "वर्टिसिलियम लेकानी (Verticillium lecanii) 5 ग्राम प्रति लीटर पानी में स्प्रे करें।"
        ],
        "chemical_safe": {
            "name": "इमिडाक्लोप्रिड 17.8% एसएल (Imidacloprid)",
            "dose": "0.5 मिली प्रति लीटर पानी (यानी 15 लीटर की टंकी में 7-8 मिली)",
            "cibrc_caution": "फूल खिलते समय छिड़काव न करें ताकि मधुमक्खियों को नुकसान न पहुंचे। अंतिम छिड़काव व कटाई में 15 दिन का अंतर रखें।"
        }
    },
    "fall_armyworm": {
        "name_hindi": "फॉल आर्मीवर्म / तना छेदक (Fall Armyworm / Borer)",
        "crops": ["मक्का", "धान", "ज्वार"],
        "symptoms": "पत्तियों में बड़े-बड़े छेद, पौधों के तने या गोभ के अंदर भूसा जैसा मल भरा रहता है, बालियां कट जाती हैं।",
        "ipm_cultural": [
            "फेरोमोन ट्रैप (Pheromone Traps) 4-5 प्रति एकड़ लगाएं।",
            "मक्का की गोभ में सूखी रेत या राख का छिड़काव करें।"
        ],
        "biological": [
            "बैसिलस थुरिंजिएंसिस (Bt) 2 ग्राम प्रति लीटर पानी में छिड़कें।",
            "बिवेरिया बैसियाना (Beauveria bassiana) 5 ग्राम प्रति लीटर।"
        ],
        "chemical_safe": {
            "name": "क्लोरांट्रानिलीप्रोल 18.5% एससी (Coragen)",
            "dose": "0.4 मिली प्रति लीटर पानी (15 लीटर की टंकी में 6 मिली)",
            "cibrc_caution": "दवा का छिड़काव सीधे पौधे की गोभ (Whorl) में करें। सुरक्षा दस्ताने व मास्क अवश्य पहनें।"
        }
    },
    "whitefly": {
        "name_hindi": "सफेद मक्खी (Whitefly)",
        "crops": ["कपास", "टमाटर", "मिर्च", "भिंडी"],
        "symptoms": "पत्तियों की निचली सतह पर सफेद रंग के छोटे पतंगे उड़ते हैं। पत्तियां ऊपर की तरफ मुड़ती हैं और पीला मोजेक वायरस फैलता है।",
        "ipm_cultural": [
            "पीले स्टिकी ट्रैप (Yellow Sticky Traps) लगाएं।",
            "नाइट्रोजन खाद (यूरिया) का अत्यधिक प्रयोग बंद करें।"
        ],
        "biological": [
            "नीम का काढ़ा या नीमास्त्र 100% सांद्रता में सुबह-सुबह स्प्रे करें।"
        ],
        "chemical_safe": {
            "name": "डायफेंथियूरॉन 50% डब्ल्यूपी (Diafenthiuron)",
            "dose": "1.2 ग्राम प्रति लीटर पानी",
            "cibrc_caution": "तेज धूप और दोपहर में स्प्रे न करें। सुबह या शाम के समय पत्तियों के निचले हिस्से पर स्प्रे करें।"
        }
    },
    "caterpillar": {
        "name_hindi": "फल छेदक / तंबाकू इल्ली (Pod Borer / Spodoptera)",
        "crops": ["चना", "टमाटर", "अरहर", "सोयाबीन"],
        "symptoms": "इल्ली फल/फली में छेद करके अंदर का भाग खाती है, फली पर गोल छेद और विष्ठा दिखाई देती है।",
        "ipm_cultural": [
            "टी-आकार की खूंटियां (Bird Perches) 20 प्रति एकड़ लगाएं ताकि पक्षी बैठकर इल्लियों को खा सकें।",
            "हेलिकोवर्पा फेरोमोन ट्रैप 5 प्रति एकड़ लगाएं।"
        ],
        "biological": [
            "हाइपेरिया/NPV वायरस 250 LE प्रति हेक्टेयर या नीम बीज अर्क (NSKE 5%) का स्प्रे करें।"
        ],
        "chemical_safe": {
            "name": "एमामेक्टिन बेंजोएट 5% एसजी (Emamectin Benzoate)",
            "dose": "0.5 ग्राम प्रति लीटर पानी (15 लीटर टंकी में 7-8 ग्राम)",
            "cibrc_caution": "जल स्रोतों के पास बर्तन न धोएं। हवा के विपरीत दिशा में छिड़काव न करें।"
        }
    }
}

def get_pest_advisory(pest_or_symptom: str, crop: str = "") -> Dict[str, Any]:
    text_lower = (pest_or_symptom + " " + crop).lower()
    
    selected_key = "aphids"
    for k in PEST_CATALOG.keys():
        if k in text_lower or (k == "fall_armyworm" and ("army" in text_lower or "borer" in text_lower or "कीड़ा" in text_lower or "इल्ली" in text_lower)):
            selected_key = k
            break
        elif "सफेद" in text_lower or "मक्खी" in text_lower or "white" in text_lower:
            selected_key = "whitefly"
            break
        elif "इल्ली" in text_lower or "छेदक" in text_lower or "सुंडी" in text_lower or "चना" in text_lower:
            selected_key = "caterpillar"
            break
            
    info = PEST_CATALOG[selected_key]
    return {
        "pest_name": info["name_hindi"],
        "target_crops": info["crops"],
        "symptoms": info["symptoms"],
        "integrated_pest_management": {
            "cultural_traps": info["ipm_cultural"],
            "biological_organic": info["biological"]
        },
        "chemical_solution": info["chemical_safe"],
        "expert_recommendation": f"कीट के शुरुआती प्रकोप पर सबसे पहले नीम आधारित कीटनाशक (जैविक) व ट्रैप का उपयोग करें। यदि संक्रमण 10-15% से अधिक (ETL पार) हो, तभी संस्तुत रासायनिक दवा का नियत मात्रा में छिड़काव करें।"
    }
