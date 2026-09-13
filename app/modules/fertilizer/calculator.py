from typing import Dict, Any, List

CROP_NPK_REQUIREMENTS = {
    "wheat": {"name": "गेहूं", "name_en": "Wheat", "N": 120.0, "P": 60.0, "K": 40.0, "organic_opt": "वर्मीकम्पोस्ट + जीवामृत", "organic_opt_en": "Vermicompost + Jeevamrut"},
    "rice": {"name": "धान", "name_en": "Rice / Paddy", "N": 120.0, "P": 60.0, "K": 60.0, "organic_opt": "हरी खाद (ढैंचा) + एजोला", "organic_opt_en": "Green Manuring (Sesbania) + Azolla"},
    "maize": {"name": "मक्का", "name_en": "Maize", "N": 100.0, "P": 50.0, "K": 30.0, "organic_opt": "गोबर खाद + नीम खली", "organic_opt_en": "FYM + Neem Cake"},
    "potato": {"name": "आलू", "name_en": "Potato", "N": 150.0, "P": 80.0, "K": 100.0, "organic_opt": "सड़ी गोबर खाद 10 टन", "organic_opt_en": "Decomposed Farmyard Manure 10t/ha"},
    "tomato": {"name": "टमाटर", "name_en": "Tomato", "N": 100.0, "P": 60.0, "K": 60.0, "organic_opt": "जीवामृत स्प्रे + वर्मीकम्पोस्ट", "organic_opt_en": "Jeevamrut spray + Vermicompost"},
    "cotton": {"name": "कपास", "name_en": "Cotton", "N": 120.0, "P": 60.0, "K": 60.0, "organic_opt": "अरंडी की खली + पोटाश बैक्टीरिया", "organic_opt_en": "Castor cake + Potash mobilizing bacteria"},
    "sugarcane": {"name": "गन्ना", "name_en": "Sugarcane", "N": 200.0, "P": 80.0, "K": 80.0, "organic_opt": "प्रेसमड कम्पोस्ट + ट्राइकोडर्मा", "organic_opt_en": "Pressmud compost + Trichoderma"},
    "mustard": {"name": "सरसों", "name_en": "Mustard", "N": 80.0, "P": 40.0, "K": 20.0, "organic_opt": "सल्फर 90% + गोबर खाद", "organic_opt_en": "Sulphur 90% + FYM"}
}

def calculate_fertilizer_schedule(
    crop: str = "wheat",
    soil_n: float = 220.0,
    soil_p: float = 12.0,
    soil_k: float = 150.0,
    rain_forecast_48h: bool = False,
    acres: float = 1.0
) -> Dict[str, Any]:
    crop_lower = crop.strip().lower()
    profile = CROP_NPK_REQUIREMENTS.get(crop_lower, CROP_NPK_REQUIREMENTS["wheat"])
    crop_name_hindi = profile["name"]
    crop_name_en = profile["name_en"]
    
    n_factor = 1.25 if soil_n < 280 else (0.85 if soil_n > 560 else 1.0)
    p_factor = 1.30 if soil_p < 10 else (0.80 if soil_p > 25 else 1.0)
    k_factor = 1.20 if soil_k < 110 else (0.80 if soil_k > 280 else 1.0)
    
    req_n_ha = profile["N"] * n_factor
    req_p_ha = profile["P"] * p_factor
    req_k_ha = profile["K"] * k_factor
    
    req_n = (req_n_ha / 2.47) * acres
    req_p = (req_p_ha / 2.47) * acres
    req_k = (req_k_ha / 2.47) * acres
    
    dap_kg = req_p / 0.46
    n_from_dap = dap_kg * 0.18
    remaining_n = max(0.0, req_n - n_from_dap)
    urea_kg = remaining_n / 0.46
    mop_kg = req_k / 0.60
    
    dap_bags = round(dap_kg / 50.0, 1)
    urea_bags = round(urea_kg / 45.0, 1)
    mop_bags = round(mop_kg / 50.0, 1)
    
    weather_alert_hi = None
    weather_alert_en = None
    if rain_forecast_48h:
        weather_alert_hi = "⚠️ मौसम चेतावनी: अगले 48 घंटों में वर्षा की संभावना है। यूरिया (नाइट्रोजन) का टॉप ड्रेसिंग छिड़काव तुरंत टाल दें, अन्यथा पानी के साथ बहकर भारी नुकसान होगा।"
        weather_alert_en = "⚠️ Weather Alert: Rain forecast within next 48 hours. Postpone urea top-dressing to prevent leaching losses."

    schedule = [
        {
            "stage": "बुवाई/रोपाई के समय (Basal Dose)",
            "stage_en": "Basal Application (At Sowing/Transplanting)",
            "fertilizer": f"DAP: {round(dap_kg, 1)} किग्रा ({dap_bags} बोरी) + MOP: {round(mop_kg, 1)} किग्रा ({mop_bags} बोरी)",
            "fertilizer_en": f"DAP: {round(dap_kg, 1)} kg ({dap_bags} bags) + MOP: {round(mop_kg, 1)} kg ({mop_bags} bags)",
            "instructions": "जुताई के समय आखिरी पाटा लगाने से पहले कूंड़ में गहराई पर डालें।",
            "instructions_en": "Place in furrows below seed level before final leveling."
        },
        {
            "stage": "पहली सिंचाई पर (First Irrigation / 21-25 दिन बाद)",
            "stage_en": "1st Irrigation (CRI stage / 21-25 days)",
            "fertilizer": f"यूरिया: {round(urea_kg * 0.5, 1)} किग्रा ({round(urea_bags * 0.5, 1)} बोरी) + जिंक 5 किग्रा",
            "fertilizer_en": f"Urea: {round(urea_kg * 0.5, 1)} kg ({round(urea_bags * 0.5, 1)} bags) + Zinc Sulphate 5kg",
            "instructions": "सिंचाई करने के 1-2 दिन बाद ओट आने पर बिखेरें।",
            "instructions_en": "Broadcast 1-2 days after irrigation when soil is at field capacity."
        },
        {
            "stage": "दूसरी सिंचाई पर (Tillering / कल्ले फूटने पर / 45 दिन)",
            "stage_en": "2nd Irrigation (Tillering / 45 days)",
            "fertilizer": f"यूरिया: {round(urea_kg * 0.5, 1)} किग्रा ({round(urea_bags * 0.5, 1)} बोरी)",
            "fertilizer_en": f"Urea: {round(urea_kg * 0.5, 1)} kg ({round(urea_bags * 0.5, 1)} bags)",
            "instructions": "शाम के समय डालें और आवश्यकतानुसार हल्की सिंचाई करें।",
            "instructions_en": "Apply in late evening followed by light irrigation if needed."
        }
    ]
    
    organic_recommendation = {
        "title": "प्राकृतिक एवं जैविक विकल्प (INM / Organic)",
        "title_en": "Organic & Natural Farming Options",
        "inputs": [
            f"{profile['organic_opt']} - मिट्टी में जीवांश बढ़ाने के लिए अत्यंत लाभकारी।",
            "जीवामृत (Jeevamrut): 200 लीटर प्रति एकड़ सिंचाई के पानी के साथ चलाएं।",
            "नीम की खली (Neem Cake): 50 किग्रा प्रति एकड़ जुताई में मिलाएं।"
        ],
        "inputs_en": [
            f"{profile['organic_opt_en']} - High efficacy for soil organic matter restoration.",
            "Jeevamrut: Apply 200 litres per acre through irrigation water.",
            "Neem Cake: Mix 50 kg/acre into soil during plowing for nematode and grub suppression."
        ]
    }

    return {
        "crop": crop_name_hindi,
        "crop_en": crop_name_en,
        "acres": acres,
        "soil_context": {"N": soil_n, "P": soil_p, "K": soil_k},
        "weather_alert": weather_alert_hi,
        "weather_alert_en": weather_alert_en,
        "recommendation_bags": {
            "dap_bags_50kg": dap_bags,
            "dap_kg": round(dap_kg, 1),
            "urea_bags_45kg": urea_bags,
            "urea_kg": round(urea_kg, 1),
            "mop_bags_50kg": mop_bags,
            "mop_kg": round(mop_kg, 1)
        },
        "application_schedule": schedule,
        "organic_plan": organic_recommendation
    }
