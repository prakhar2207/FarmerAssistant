from typing import Dict, Any, List

# Standard crop nutrient requirements in kg/hectare (N, P, K)
CROP_NPK_REQUIREMENTS = {
    "wheat": {"name": "गेहूं", "N": 120.0, "P": 60.0, "K": 40.0, "organic_opt": "वर्मीकम्पोस्ट + जीवामृत"},
    "rice": {"name": "धान", "N": 120.0, "P": 60.0, "K": 60.0, "organic_opt": "हरी खाद (ढैंचा) + एजोला"},
    "maize": {"name": "मक्का", "N": 100.0, "P": 50.0, "K": 30.0, "organic_opt": "गोबर खाद + नीम खली"},
    "potato": {"name": "आलू", "N": 150.0, "P": 80.0, "K": 100.0, "organic_opt": "सड़ी गोबर खाद 10 टन"},
    "tomato": {"name": "टमाटर", "N": 100.0, "P": 60.0, "K": 60.0, "organic_opt": "जीवामृत स्प्रे + वर्मीकम्पोस्ट"},
    "cotton": {"name": "कपास", "N": 120.0, "P": 60.0, "K": 60.0, "organic_opt": "अरंडी की खली + पोटाश बैक्टीरिया"},
    "sugarcane": {"name": "गन्ना", "N": 200.0, "P": 80.0, "K": 80.0, "organic_opt": "प्रेसमड कम्पोस्ट + ट्राइकोडर्मा"},
    "mustard": {"name": "सरसों", "N": 80.0, "P": 40.0, "K": 20.0, "organic_opt": "सल्फर 90% + गोबर खाद"}
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
    
    # Deficit adjustment factor (1 hectare = 2.47 acres)
    # Soil fertility factors
    n_factor = 1.25 if soil_n < 280 else (0.85 if soil_n > 560 else 1.0)
    p_factor = 1.30 if soil_p < 10 else (0.80 if soil_p > 25 else 1.0)
    k_factor = 1.20 if soil_k < 110 else (0.80 if soil_k > 280 else 1.0)
    
    req_n_ha = profile["N"] * n_factor
    req_p_ha = profile["P"] * p_factor
    req_k_ha = profile["K"] * k_factor
    
    # Conversion to per acre:
    req_n = (req_n_ha / 2.47) * acres
    req_p = (req_p_ha / 2.47) * acres
    req_k = (req_k_ha / 2.47) * acres
    
    # DAP contains 18% N and 46% P2O5
    # MOP contains 60% K2O
    # Urea contains 46% N
    dap_kg = req_p / 0.46
    n_from_dap = dap_kg * 0.18
    remaining_n = max(0.0, req_n - n_from_dap)
    urea_kg = remaining_n / 0.46
    mop_kg = req_k / 0.60
    
    # Bags conversion: DAP (50kg bag), Urea (45kg bag), MOP (50kg bag)
    dap_bags = round(dap_kg / 50.0, 1)
    urea_bags = round(urea_kg / 45.0, 1)
    mop_bags = round(mop_kg / 50.0, 1)
    
    # Weather Safety constraint
    weather_alert = None
    if rain_forecast_48h:
        weather_alert = "⚠️ मौसम चेतावनी: अगले 48 घंटों में वर्षा की संभावना है। यूरिया (नाइट्रोजन) का टॉप ड्रेसिंग छिड़काव तुरंत टाल दें, अन्यथा पानी के साथ बहकर भारी नुकसान होगा।"

    schedule = [
        {
            "stage": "बुवाई/रोपाई के समय (Basal Dose)",
            "fertilizer": f"DAP: {round(dap_kg, 1)} किग्रा (लगभग {dap_bags} बोरी) + MOP: {round(mop_kg, 1)} किग्रा ({mop_bags} बोरी)",
            "instructions": "जुताई के समय आखिरी पाटा लगाने से पहले कूंड़ में गहराई पर डालें।"
        },
        {
            "stage": "पहली सिंचाई पर (First Irrigation / 21-25 दिन बाद)",
            "fertilizer": f"यूरिया: {round(urea_kg * 0.5, 1)} किग्रा (लगभग {round(urea_bags * 0.5, 1)} बोरी) + जिंक सल्फेट 5 किग्रा",
            "instructions": "सिंचाई करने के 1-2 दिन बाद ओट आने पर बिखेरें।"
        },
        {
            "stage": "दूसरी सिंचाई पर (Tillering / कल्ले फूटने पर / 45 दिन)",
            "fertilizer": f"यूरिया: {round(urea_kg * 0.5, 1)} किग्रा (लगभग {round(urea_bags * 0.5, 1)} बोरी)",
            "instructions": "शाम के समय डालें और आवश्यकतानुसार हल्की सिंचाई करें।"
        }
    ]
    
    organic_recommendation = {
        "title": "प्राकृतिक एवं जैविक विकल्प (INM / Organic)",
        "inputs": [
            f"{profile['organic_opt']} - मिट्टी में जीवांश बढ़ाने के लिए अत्यंत लाभकारी।",
            "जीवामृत (Jeevamrut): 200 लीटर प्रति एकड़ सिंचाई के पानी के साथ चलाएं।",
            "नीम की खली (Neem Cake): 50 किग्रा प्रति एकड़ जुताई में मिलाने से दीमक व सफेद गिडार से सुरक्षा मिलती है।"
        ]
    }

    return {
        "crop": crop_name_hindi,
        "acres": acres,
        "soil_context": {"N": soil_n, "P": soil_p, "K": soil_k},
        "weather_alert": weather_alert,
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
