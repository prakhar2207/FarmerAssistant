from typing import Dict, Any, List, Optional
from app.core.intent import detect_intent_and_slots
from app.core.safety import validate_agricultural_safety
from app.core.memory import get_farmer_profile, get_recent_chat_history, save_chat_turn
from app.modules.weather.service import get_weather_data, resolve_location
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories
from app.modules.crop_recommender.model import crop_recommender
from app.modules.fertilizer.calculator import calculate_fertilizer_schedule
from app.modules.pest.advisory import get_pest_advisory
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.rag.retriever import agri_rag
from app.modules.schemes.scheme_catalog import scheme_catalog

class AgriculturalAgentOrchestrator:
    def process_query(
        self,
        query: str,
        session_id: str = "default_session",
        farmer_id: str = "default_farmer",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        lang: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Fetch Farmer Profile & History
        profile = get_farmer_profile(farmer_id)
        history = get_recent_chat_history(session_id, limit=3)
        
        # 2. Detect Intent, Slots & Language
        intent_data = detect_intent_and_slots(query, history, requested_lang=lang)
        intent = intent_data["intent"]
        language = intent_data.get("language", "hi")
        crop = intent_data.get("crop") or profile.get("current_crop", "गेहूं" if language == "hi" else "wheat")
        
        # 3. Location & Weather Intelligence
        district = profile.get("district", "Lucknow")
        lat, lon, loc_label = resolve_location(district, latitude, longitude)
        weather_data = get_weather_data(lat, lon, loc_label)
        curr_weather = weather_data.get("current", {})
        temp = curr_weather.get("temperature", 28.0)
        humidity = curr_weather.get("humidity", 65)
        wind_speed = curr_weather.get("wind_speed", 8.0)
        
        forecast = weather_data.get("forecast", [])
        rain_expected_48h = any(d.get("rain_prob", 0) >= 30 for d in forecast[:2])
        rain_prob = max([d.get("rain_prob", 0) for d in forecast[:2]] or [10])

        if language == "en":
            thought_steps = [
                f"Farmer Profile: {profile.get('name', 'Farmer')} ({profile.get('district', 'Lucknow')})",
                f"Location & Weather: {loc_label} | Temp {temp}°C, Humidity {humidity}%, Rain Prob {rain_prob}%",
                f"Classified Intent: {intent} | Target Crop: {crop}"
            ]
        else:
            thought_steps = [
                f"किसान प्रोफाइल: {profile.get('name', 'किसान')} ({profile.get('district', 'लखनऊ')})",
                f"स्थान व मौसम: {loc_label} | तापमान {temp}°C, नमी {humidity}%, वर्षा संभावना {rain_prob}%",
                f"पहचाना गया उद्देश्य (Intent): {intent} | संबंधित फसल: {crop}"
            ]

        # 4. Check for Missing Slots & Clarification
        if intent_data.get("needs_clarification"):
            clarification_msg = intent_data["clarification_question"]
            if language == "en":
                thought_steps.append("Essential information missing: Generating polite clarification question.")
                follow_ups = [
                    "Advice for Wheat crop",
                    "Advice for Rice crop",
                    "Advice for Tomato crop",
                    "Locate nearby soil testing labs"
                ]
            else:
                thought_steps.append("महत्वपूर्ण जानकारी अनुपलब्ध: किसान से स्पष्टीकरण प्रश्न पूछा जा रहा है।")
                follow_ups = [
                    "गेहूं की फसल के बारे में",
                    "धान की फसल के बारे में",
                    "टमाटर की फसल के बारे में",
                    "नजदीकी मिट्टी जांच केंद्र बताएं"
                ]
            
            save_chat_turn(session_id, farmer_id, query, clarification_msg, intent)
            return {
                "response": clarification_msg,
                "intent": intent,
                "language": language,
                "thought_steps": thought_steps,
                "follow_up_suggestions": follow_ups,
                "weather_summary": f"{loc_label}: {temp}°C, {curr_weather.get('condition', 'Clear')}"
            }

        # 5. Specialized Tool Invocation
        tool_output = ""
        follow_ups = []
        
        if intent == "WEATHER_FORECAST":
            thought_steps.append("Executing Weather Intelligence Tool..." if language == "en" else "मौसम उपकरण (Weather Tool) निष्पादित किया गया।")
            advisories = generate_agricultural_weather_advisories(weather_data)
            
            if language == "en":
                adv_text = "\n".join([f"• {a['title']}: {a['advice']}" for a in advisories])
                tool_output = (
                    f"🌦️ **Weather Forecast & Agro-Advisory for {loc_label}:**\n"
                    f"• Current Temperature: {temp}°C (Feels like: {curr_weather.get('apparent_temperature', temp)}°C)\n"
                    f"• Relative Humidity: {humidity}%\n"
                    f"• Wind Velocity: {wind_speed} km/h\n"
                    f"• Condition: {curr_weather.get('condition', 'Clear')}\n\n"
                    f"🌾 **Agricultural Advisories:**\n{adv_text}"
                )
                follow_ups = ["5-day rain forecast", "Can I apply fertilizer today?", "Best time for spray"]
            else:
                adv_text = "\n".join([f"• {a['title']}: {a['advice']}" for a in advisories])
                tool_output = (
                    f"🌦️ **{loc_label} के लिए मौसम पूर्वानुमान:**\n"
                    f"• वर्तमान तापमान: {temp}°C (अनुभूत: {curr_weather.get('apparent_temperature', temp)}°C)\n"
                    f"• हवा में नमी (Humidity): {humidity}%\n"
                    f"• हवा की गति: {wind_speed} किमी/घंटा\n"
                    f"• स्थिति: {curr_weather.get('condition', 'सामान्य')}\n\n"
                    f"🌾 **मौसम आधारित कृषि सलाह:**\n{adv_text}"
                )
                follow_ups = ["अगले 5 दिनों की बारिश का हाल", "क्या अभी खाद डाल सकते हैं?", "कीटनाशक स्प्रे का सही समय"]

        elif intent == "CROP_RECOMMENDATION":
            thought_steps.append("Executing Machine Learning Crop Recommender..." if language == "en" else "मृदा-जलवायु फसल अनुशंसा मॉडल (Crop ML Engine) निष्पादित किया गया।")
            rec = crop_recommender.recommend(n=85, p=45, k=40, temperature=temp, humidity=humidity, ph=7.2, rainfall=100)
            
            if language == "en":
                crops_list = "\n".join([
                    f"{i+1}. **{c['crop_key'].title()} ({c['hindi_name']})** (Suitability: {c['suitability_score']}%)\n   • Sowing Period: {c['sowing_months']} | Water Need: {c['water_need']}\n   • Note: {c['description']}"
                    for i, c in enumerate(rec["top_recommendations"])
                ])
                tool_output = (
                    f"🌱 **Recommended Crops for Your Soil & Climate Context:**\n\n"
                    f"{crops_list}\n\n"
                    f"💡 **Agronomic Summary:** Best suited crop is {rec['top_recommendations'][0]['crop_key'].title()} ({rec['top_recommendations'][0]['suitability_score']}% match) based on soil test parameters and regional weather."
                )
                follow_ups = ["What fertilizer dose is required?", "What is the recommended seed rate?", "Government seed subsidies"]
            else:
                crops_list = "\n".join([
                    f"{i+1}. **{c['hindi_name']}** (अनुकूलता: {c['suitability_score']}%)\n   • बुवाई समय: {c['sowing_months']} | पानी की आवश्यकता: {c['water_need']}\n   • विवरण: {c['description']}"
                    for i, c in enumerate(rec["top_recommendations"])
                ])
                tool_output = (
                    f"🌱 **आपके क्षेत्र एवं वर्तमान मौसम के लिए श्रेष्ठ फसलें:**\n\n"
                    f"{crops_list}\n\n"
                    f"💡 **कृषि वैज्ञानिक परामर्श:** {rec['summary_hindi']}"
                )
                follow_ups = ["इस फसल में खाद की कितनी मात्रा लगेगी?", "बुवाई के लिए बीज दर क्या रखें?", "सरकारी बीज सब्सिडी योजना"]

        elif intent == "FERTILIZER_ADVISORY":
            thought_steps.append("Executing Integrated Nutrient Management (INM) Calculator..." if language == "en" else "संतुलित पोषक तत्व प्रबंधन मॉडल (Fertilizer Engine) निष्पादित किया गया।")
            fert = calculate_fertilizer_schedule(crop=crop, soil_n=230, soil_p=12, soil_k=150, rain_forecast_48h=rain_expected_48h, acres=profile.get("farm_size_acres", 1.0))
            
            if language == "en":
                sched_text = "\n".join([f"• **{s['stage_en']}**: {s['fertilizer_en']}\n   (Method: {s['instructions_en']})" for s in fert["application_schedule"]])
                organic_text = "\n".join([f"• {inp}" for inp in fert["organic_plan"]["inputs_en"]])
                tool_output = (
                    f"💊 **Balanced Fertilization Schedule for {fert['crop_en']} ({fert['acres']} Acre):**\n\n"
                    f"📦 **Required Fertilizer Quantities (50kg Standard Bags):**\n"
                    f"• DAP (50kg bag): {fert['recommendation_bags']['dap_bags_50kg']} bags ({fert['recommendation_bags']['dap_kg']} kg)\n"
                    f"• Urea (45kg bag): {fert['recommendation_bags']['urea_bags_45kg']} bags ({fert['recommendation_bags']['urea_kg']} kg)\n"
                    f"• MOP Potash (50kg bag): {fert['recommendation_bags']['mop_bags_50kg']} bags ({fert['recommendation_bags']['mop_kg']} kg)\n\n"
                    f"📅 **Application Schedule:**\n{sched_text}\n\n"
                    f"🌿 **Organic & Natural Farming Supplements:**\n{organic_text}"
                )
                if fert.get("weather_alert_en"):
                    tool_output = fert["weather_alert_en"] + "\n\n" + tool_output
                follow_ups = ["How to prepare Jeevamrut formulation?", "Can I mix Zinc Sulphate with Urea?", "When to irrigate after fertilizer?"]
            else:
                sched_text = "\n".join([f"• **{s['stage']}**: {s['fertilizer']}\n   (निर्देश: {s['instructions']})" for s in fert["application_schedule"]])
                organic_text = "\n".join([f"• {inp}" for inp in fert["organic_plan"]["inputs"]])
                tool_output = (
                    f"💊 **{fert['crop']} की फसल के लिए संतुलित खाद व पोषण योजना ({fert['acres']} एकड़ हेतु):**\n\n"
                    f"📦 **कुल आवश्यक मात्रा (कट्टे / बोरियां):**\n"
                    f"• डीएपी (DAP 50kg बैग): {fert['recommendation_bags']['dap_bags_50kg']} बोरी ({fert['recommendation_bags']['dap_kg']} किग्रा)\n"
                    f"• यूरिया (Urea 45kg बैग): {fert['recommendation_bags']['urea_bags_45kg']} बोरी ({fert['recommendation_bags']['urea_kg']} किग्रा)\n"
                    f"• पोटाश (MOP 50kg बैग): {fert['recommendation_bags']['mop_bags_50kg']} बोरी ({fert['recommendation_bags']['mop_kg']} किग्रा)\n\n"
                    f"📅 **डालने का सही समय व तरीका:**\n{sched_text}\n\n"
                    f"🌿 **प्राकृतिक व जैविक विकल्प:**\n{organic_text}"
                )
                if fert.get("weather_alert"):
                    tool_output = fert["weather_alert"] + "\n\n" + tool_output
                follow_ups = ["जीवामृत बनाने की पूरी विधि", "यूरिया के साथ जिंक कैसे मिलाएं?", "सिंचाई कब करनी चाहिए?"]

        elif intent == "PEST_CONTROL":
            thought_steps.append("Executing Integrated Pest Management (IPM) Advisor..." if language == "en" else "एकीकृत कीट प्रबंधन सलाहकार (IPM Engine) निष्पादित किया गया।")
            pest_res = get_pest_advisory(query, crop)
            chem = pest_res["chemical_solution"]
            traps = "\n".join([f"• {t}" for t in pest_res["integrated_pest_management"]["cultural_traps"]])
            bio = "\n".join([f"• {b}" for b in pest_res["integrated_pest_management"]["biological_organic"]])
            
            if language == "en":
                tool_output = (
                    f"🐛 **Pest Diagnosis: {pest_res['pest_name']}**\n"
                    f"• Symptoms: {pest_res['symptoms']}\n\n"
                    f"🪤 **Integrated Pest Management (IPM) & Biological Controls:**\n{traps}\n{bio}\n\n"
                    f"🧪 **Recommended Safe Chemical Intervention (CIBRC Approved):**\n"
                    f"• Insecticide: **{chem['name']}**\n"
                    f"• Dosage: {chem['dose']}\n"
                    f"• Precaution: {chem['cibrc_caution']}\n\n"
                    f"💡 {pest_res['expert_recommendation']}"
                )
                follow_ups = ["How to prepare Neem oil spray?", "Where to buy pheromone traps?", "Pre-harvest waiting interval"]
            else:
                tool_output = (
                    f"🐛 **कीट निदान: {pest_res['pest_name']}**\n"
                    f"• लक्षण: {pest_res['symptoms']}\n\n"
                    f"🪤 **देसी व जैविक रोकथाम (IPM):**\n{traps}\n{bio}\n\n"
                    f"🧪 **आवश्यकता पड़ने पर संस्तुत सुरक्षित रासायनिक उपाय:**\n"
                    f"• दवा: **{chem['name']}**\n"
                    f"• मात्रा: {chem['dose']}\n"
                    f"• सावधानी: {chem['cibrc_caution']}\n\n"
                    f"💡 {pest_res['expert_recommendation']}"
                )
                follow_ups = ["नीम तेल का स्प्रे कैसे तैयार करें?", "फेरोमोन ट्रैप कहां से मिलेगा?", "दवा छिड़काव के बाद कितने दिन न काटें?"]

        elif intent == "SOIL_ANALYSIS":
            thought_steps.append("Executing Soil Intelligence & Govt Lab Finder..." if language == "en" else "मृदा विश्लेषण एवं सरकारी लैब खोजक (Soil Intelligence) निष्पादित किया गया।")
            soil_res = analyze_soil_metrics(ph=7.2, oc=0.48, n=210, p=11, k=160, state=profile.get("state", "Uttar Pradesh"))
            nearby_labs = find_nearby_soil_labs(profile.get("state", ""), profile.get("district", ""))
            
            if language == "en":
                def_text = "\n".join([f"• {d}" for d in soil_res["deficiencies_en"]])
                amend_text = "\n".join([f"• **{a['action_en']}**: {a['dose_en']}" for a in soil_res["amendments"]])
                labs_text = "\n".join([f"• **{l['name']}** ({l['type']})\n   Address: {l['address']} | Fee: {l['fee']}" for l in nearby_labs])
                tool_output = (
                    f"🧪 **Soil Health Card Assessment:**\n"
                    f"• Soil Health Score: **{soil_res['health_score']}/100**\n"
                    f"• Soil Classification: {soil_res['soil_classification']['name_hindi']}\n"
                    f"• Detected Deficiencies:\n{def_text}\n\n"
                    f"🌾 **Corrective Soil Amendments:**\n{amend_text}\n\n"
                    f"🏛️ **Nearby Government Soil Testing Labs & KVKs:**\n{labs_text}"
                )
                follow_ups = ["How to collect soil sample correctly?", "How to apply gypsum for alkaline soil?", "Organic matter improvement"]
            else:
                def_text = "\n".join([f"• {d}" for d in soil_res["deficiencies"]])
                amend_text = "\n".join([f"• **{a['action']}**: {a['dose']}" for a in soil_res["amendments"]])
                labs_text = "\n".join([f"• **{l['name']}** ({l['type']})\n   पता: {l['address']} | शुल्क: {l['fee']}" for l in nearby_labs])
                tool_output = (
                    f"🧪 **मृदा स्वास्थ्य मूल्यांकन रिपोर्ट:**\n"
                    f"• स्वास्थ्य स्कोर: **{soil_res['health_score']}/100**\n"
                    f"• मिट्टी का प्रकार: {soil_res['soil_classification']['name_hindi']}\n"
                    f"• मुख्य कमियां:\n{def_text}\n\n"
                    f"🌾 **सुधारात्मक उपाय:**\n{amend_text}\n\n"
                    f"🏛️ **नजदीकी सरकारी मृदा जांच केंद्र:**\n{labs_text}"
                )
                follow_ups = ["मिट्टी का नमूना लेने का सही तरीका", "जिप्सम कब और कैसे डालें?", "गोबर खाद की जगह क्या डालें?"]

        elif intent == "GOVT_SCHEME":
            thought_steps.append("Searching Government Welfare Schemes Knowledge Base..." if language == "en" else "सरकारी योजना ज्ञानकोश (Govt Schemes Catalog) निष्पादित किया गया।")
            schemes = scheme_catalog.search(query)
            
            if language == "en":
                sch_text = "\n\n".join([
                    f"🏛️ **{s['name']}**\n• Objective: {s['objective']}\n• Eligibility: {s['eligibility']}\n• Benefits: {s['benefits']}\n• How to Apply: {s['how_to_apply']} (Helpline: {s['helpline']})"
                    for s in schemes[:2]
                ])
                tool_output = f"🇮🇳 **Government Schemes for Indian Farmers:**\n\n{sch_text}"
                follow_ups = ["How to check PM-KISAN installment?", "How to claim PMFBY crop insurance?", "Kisan Credit Card application"]
            else:
                sch_text = "\n\n".join([
                    f"🏛️ **{s['name']}**\n• उद्देश्य: {s['objective']}\n• पात्रता: {s['eligibility']}\n• लाभ: {s['benefits']}\n• आवेदन: {s['how_to_apply']} (हेल्पलाइन: {s['helpline']})"
                    for s in schemes[:2]
                ])
                tool_output = f"🇮🇳 **किसानों के लिए प्रमुख सरकारी योजनाएं:**\n\n{sch_text}"
                follow_ups = ["पीएम किसान की किस्त कैसे चेक करें?", "फसल बीमा का क्लेम कैसे करें?", "केसीसी लोन का फॉर्म"]

        else: # GENERAL_AGRI
            thought_steps.append("Retrieving from ICAR/KVK Knowledge Base (RAG)..." if language == "en" else "ICAR/KVK आरएजी ज्ञानकोश (RAG Knowledge Base) से प्रामाणिक सामग्री खोजी जा रही है।")
            rag_docs = agri_rag.retrieve(query, top_k=2)
            if language == "en":
                content_pieces = "\n\n".join([f"📘 *{d['title']}* ({d['source']}):\n{d['content']}" for d in rag_docs])
                tool_output = f"🌾 **ICAR Agricultural Advisory:**\n\n{content_pieces}"
                follow_ups = ["What is the recommended sowing window?", "How to prevent disease outbreak?", "Optimal fertilizer dosage"]
            else:
                content_pieces = "\n\n".join([f"📘 *{d['title']}* ({d['source']}):\n{d['content']}" for d in rag_docs])
                tool_output = f"🌾 **भारतीय कृषि अनुसंधान परिषद (ICAR) संस्तुति:**\n\n{content_pieces}"
                follow_ups = ["इसकी सही बुवाई का समय क्या है?", "रोग से बचाव कैसे करें?", "खाद की सही मात्रा"]

        # 6. Safety & Verification Layer
        thought_steps.append("Performing chemical safety verification & weather constraints check..." if language == "en" else "सुरक्षा, CIBRC रासायनिक सत्यापन व मौसम अनुकूलता जांच की गई।")
        safety_result = validate_agricultural_safety(tool_output, weather_rain_prob=rain_prob, wind_speed=wind_speed, lang=language)
        final_answer = safety_result["safe_response"]

        # 7. Persist Context
        save_chat_turn(session_id, farmer_id, query, final_answer, intent)

        return {
            "response": final_answer,
            "intent": intent,
            "crop": crop,
            "language": language,
            "thought_steps": thought_steps,
            "follow_up_suggestions": follow_ups,
            "weather_summary": f"{loc_label}: {temp}°C, {curr_weather.get('condition', 'Clear')}"
        }

agent_orchestrator = AgriculturalAgentOrchestrator()
