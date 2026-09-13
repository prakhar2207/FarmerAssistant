import os
from typing import Dict, Any, List, Optional, Generator
from app.core.agent_state import AgentState
from app.core.intent import detect_intent_and_slots
from app.core.safety import validate_agricultural_safety, check_query_for_banned_chemicals
from app.core.memory import get_farmer_profile, get_recent_chat_history, save_chat_turn
from app.modules.weather.service import get_weather_data, resolve_location
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories
from app.modules.crop_recommender.model import crop_recommender
from app.modules.fertilizer.calculator import calculate_fertilizer_schedule
from app.modules.pest.advisory import get_pest_advisory
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.parser import extract_soil_metrics_from_text
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.rag.retriever import agri_rag
from app.modules.schemes.scheme_catalog import scheme_catalog
from app.modules.disease.yolo_service import yolo_leaf_service

class AgriculturalAgentGraph:
    """
    Explicit State Machine / Graph Orchestrator for KrishiSaathi.
    Executes ordered state transitions across:
    1. Query Analysis & Slot Extraction
    2. Pre-execution CIBRC Chemical Safety Guardrail
    3. Multimodal YOLO Computer Vision
    4. Missing Slot Clarification Check
    5. Agro-Climatic & Weather Context Resolution
    6. Domain Tool Execution (Crop ML, Fertilizer, Soil, Schemes)
    7. Dense Semantic ICAR RAG Grounding
    8. Post-execution Safety, Weather-Spray Rules & Mandatory PPE
    9. Response Synthesis & Stream Generation
    """

    def node_initialize(self, state: AgentState) -> AgentState:
        state.farmer_profile = get_farmer_profile(state.farmer_id)
        state.chat_history = get_recent_chat_history(state.session_id, limit=4)
        return state

    def node_detect_intent(self, state: AgentState) -> AgentState:
        intent_data = detect_intent_and_slots(
            state.raw_query,
            history=state.chat_history,
            requested_lang=state.requested_lang
        )
        state.intent = intent_data["intent"]
        state.detected_language = intent_data.get("language", "hi")
        state.intent_confidence = intent_data.get("confidence", 0.90)
        state.missing_slots = intent_data.get("missing_slots", [])
        state.needs_clarification = intent_data.get("needs_clarification", False)
        state.clarification_question = intent_data.get("clarification_question")

        # Set or carry-forward crop
        crop_candidate = intent_data.get("crop")
        if not crop_candidate:
            crop_candidate = state.farmer_profile.get("current_crop")
        if crop_candidate:
            state.crop = crop_candidate.lower()

        state.add_badge("intent", "✓ प्रश्न का विश्लेषण", "✓ Understanding Question")
        lang = state.detected_language
        state.add_thought(
            f"✓ Intent: {state.intent} (Confidence: {int(state.intent_confidence*100)}%) | Crop: {state.crop or 'None'}"
            if lang == "en" else
            f"✓ उद्देश्य: {state.intent} (सटीकता: {int(state.intent_confidence*100)}%) | फसल: {state.crop or 'उल्लेख नहीं'}"
        )

        # Out-of-Domain Check
        if state.intent == "OUT_OF_DOMAIN":
            if lang == "en":
                msg = (
                    "🌾 **KrishiSaathi Agricultural Assistant:**\n\n"
                    "I am dedicated exclusively to agricultural advisory, crop protection, weather forecasts, "
                    "soil analysis, fertilizer schedules, and government farming schemes.\n\n"
                    "Please ask any question related to your crops, soil, pest management, or agricultural practices!"
                )
                follow_ups = ["Wheat fertilizer schedule", "Recommended crops for this season", "Check PM-KISAN status"]
            else:
                msg = (
                    "🌾 **कृषि साथी (KrishiSaathi) कृषि परामर्श:**\n\n"
                    "मैं केवल कृषि, फसल प्रबंधन, मौसम, मृदा स्वास्थ्य, कीट-रोग नियंत्रण और सरकारी किसान योजनाओं "
                    "से संबंधित परामर्श देने में सक्षम हूँ।\n\n"
                    "कृपया अपनी खेती, फसल, खाद, दवा या सरकारी योजनाओं से संबंधित प्रश्न पूछें!"
                )
                follow_ups = ["गेहूं में खाद की सही मात्रा", "इस मौसम की श्रेष्ठ फसलें", "पीएम किसान योजना की जानकारी"]

            state.final_response = msg
            state.follow_up_suggestions = follow_ups
            state.completed = True
            save_chat_turn(state.session_id, state.farmer_id, state.raw_query, msg, "OUT_OF_DOMAIN")

        return state

    def node_check_pre_safety(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        banned_check = check_query_for_banned_chemicals(state.raw_query, lang=state.detected_language)
        if banned_check and banned_check.get("is_banned"):
            state.intent = "SAFETY_BLOCKED"
            state.safety_violation = True
            state.safety_details = banned_check
            state.add_badge("safety", "⚠️ CIBRC सुरक्षा प्रतिबंध जांच", "⚠️ CIBRC Safety Filter Triggered")

            lang = state.detected_language
            state.add_thought(
                "⚠️ CIBRC Banned chemical detected in user query: returning legal alternative advisory."
                if lang == "en" else
                "⚠️ प्रतिबंधित रसायन पाया गया: CIBRC सुरक्षित विकल्प संस्तुति।"
            )
            state.final_response = banned_check["response"]
            state.citations = [{
                "source": "केंद्रीय कीटनाशक बोर्ड एवं पंजीकरण समिति (CIBRC)",
                "authority": "CIBRC",
                "title": "Banned Agrochemicals & Safe Alternatives Notification 2024",
                "relevance_score": 1.0,
                "citation_badge": "[CIBRC Safety Advisory 2024]"
            }]
            state.follow_up_suggestions = (
                ["Safe organic neem spray preparation", "Pheromone traps usage", "Safe fungicides for vegetables"]
                if lang == "en" else
                ["सुरक्षित जैविक नीम स्प्रे कैसे बनाएं?", "फेरोमोन ट्रैप का प्रयोग", "सब्जियों में सुरक्षित कीटनाशक"]
            )
            state.completed = True
            save_chat_turn(state.session_id, state.farmer_id, state.raw_query, state.final_response, "SAFETY_BLOCKED")

        return state

    def node_vision_diagnosis(self, state: AgentState) -> AgentState:
        if state.completed or not state.image_bytes:
            return state

        lang = state.detected_language
        state.add_badge("vision", "✓ YOLO पत्ती रोग निदान", "✓ YOLO Leaf Disease Detection")
        state.add_thought(
            "Executing YOLO foliar vision detector..." if lang == "en" else "YOLO पत्ती रोग निदान मॉडल निष्पादित किया गया।"
        )

        vision_res = yolo_leaf_service.infer(
            image_bytes=state.image_bytes,
            crop_hint=state.crop or "",
            rain_forecast=state.rain_expected_48h,
            lang=lang
        )
        state.vision_result = vision_res

        # Reject if not a recognized plant leaf
        if not vision_res.get("is_leaf", True):
            state.is_vision_rejected = True
            rej_msg = f"❌ {vision_res.get('rejection_reason', '')}\n\n💡 {vision_res.get('guidance', '')}"
            state.final_response = rej_msg
            state.follow_up_suggestions = (
                ["Upload clear leaf close-up photo", "Describe symptoms in text", "Contact KVK Scientist"]
                if lang == "en" else
                ["पत्ती की स्पष्ट फोटो अपलोड करें", "रोग के लक्षण लिखकर बताएं", "केवीके कृषि वैज्ञानिक से बात करें"]
            )
            state.completed = True
            save_chat_turn(state.session_id, state.farmer_id, state.raw_query, rej_msg, "VISION_REJECTED")
            return state

        # If leaf recognized, update crop
        if vision_res.get("crop_en"):
            state.crop = vision_res["crop_en"].lower()

        return state

    def node_check_clarification(self, state: AgentState) -> AgentState:
        if state.completed or state.image_bytes:
            return state

        if state.needs_clarification and state.clarification_question:
            lang = state.detected_language
            state.add_badge("clarification", "❓ स्पष्टीकरण आवश्यक", "❓ Information Clarification")
            state.add_thought(
                "Essential slot missing: requesting clarification from farmer."
                if lang == "en" else
                "महत्वपूर्ण जानकारी अनुपलब्ध: किसान से स्पष्टीकरण पूछा जा रहा है।"
            )
            state.final_response = state.clarification_question
            state.follow_up_suggestions = (
                ["Advice for Wheat crop", "Advice for Rice crop", "Advice for Tomato crop", "Locate nearby soil testing labs"]
                if lang == "en" else
                ["गेहूं की फसल के बारे में", "धान की फसल के बारे में", "टमाटर की फसल के बारे में", "नजदीकी मिट्टी जांच केंद्र बताएं"]
            )
            state.completed = True
            save_chat_turn(state.session_id, state.farmer_id, state.raw_query, state.final_response, state.intent)

        return state

    def node_resolve_agro_context(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        district = state.farmer_profile.get("district", "Lucknow")
        lat, lon, loc_label = resolve_location(district, state.latitude, state.longitude)
        state.location_label = loc_label

        weather_data = get_weather_data(lat, lon, loc_label)
        state.weather = weather_data
        curr = weather_data.get("current", {})
        state.temp = curr.get("temperature", 28.0)
        state.humidity = curr.get("humidity", 65)
        state.wind_speed = curr.get("wind_speed", 8.0)

        forecast = weather_data.get("forecast", [])
        state.rain_expected_48h = any(d.get("rain_prob", 0) >= 30 for d in forecast[:2])
        state.rain_prob = max([d.get("rain_prob", 0) for d in forecast[:2]] or [10])

        state.add_badge("weather", "✓ मौसम एवं मृदा स्थिति", "✓ Checking Weather & Soil")
        lang = state.detected_language
        state.add_thought(
            f"✓ Profile: {state.farmer_profile.get('name', 'Farmer')} ({loc_label}) | {state.temp}°C, Humidity {state.humidity}%, Rain {state.rain_prob}%"
            if lang == "en" else
            f"✓ किसान: {state.farmer_profile.get('name', 'किसान')} ({loc_label}) | {state.temp}°C, नमी {state.humidity}%, बारिश {state.rain_prob}%"
        )
        return state

    def node_execute_tools(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        lang = state.detected_language
        q = state.raw_query
        crop = state.crop or ("गेहूं" if lang == "hi" else "wheat")

        # Case 1: Multimodal Vision Diagnosis
        if state.vision_result and state.vision_result.get("success"):
            v = state.vision_result
            chem = v.get("chemical_solution", {})
            chem_name = chem.get("name", "")
            chem_dose = chem.get("dose", "")

            if lang == "en":
                state.tool_output = (
                    f"🍃 **Multimodal Foliar Diagnosis (YOLO Vision):**\n"
                    f"• **Detected Disease:** **{v['disease_name_en']}** ({v['crop_en']})\n"
                    f"• **Confidence Level:** {v['confidence_level_en']} ({v['confidence_score']}%)\n"
                    f"• **Estimated Foliar Damage:** {v['severity_percentage']}%\n\n"
                    f"🔍 **Symptoms:** {v['symptoms_en']}\n"
                    f"🔬 **Pathogen / Cause:** {v['pathogen_cause_en']}\n\n"
                    f"🌿 **Cultural & Biological Control (IPM):**\n"
                    f"• {v['immediate_cultural_action_en']}\n"
                    f"• {v['organic_ipm_remedy_en']}\n\n"
                    f"🧪 **Recommended Chemical Intervention (CIBRC Approved):**\n"
                    f"• Chemical: **{chem_name}**\n"
                    f"• Dosage: {chem_dose}\n\n"
                    f"{v['weather_spray_advisory_en']}"
                )
                if v.get("needs_symptom_clarification"):
                    qs = "\n".join([f"• {item}" for item in v.get("clarifying_questions", [])])
                    state.tool_output += f"\n\n❓ **Clinical Symptom Confirmation:**\nTo confirm this diagnosis, please check:\n{qs}"
                state.follow_up_suggestions = ["Best time for spray application", "Safe waiting interval before harvest", "Organic neem alternatives"]
            else:
                state.tool_output = (
                    f"🍃 **पत्ती रोग विश्लेषण (YOLO Vision Detection):**\n"
                    f"• **पहचाना गया रोग:** **{v['disease_name_hindi']}** ({v['crop']})\n"
                    f"• **विश्वसनीयता स्तर:** {v['confidence_level']} ({v['confidence_score']}%)\n"
                    f"• **संक्रमित पत्ती का अनुमानित भाग:** {v['severity_percentage']}%\n\n"
                    f"🔍 **रोग के लक्षण:** {v['symptoms']}\n"
                    f"🔬 **कारक व अनुकूल मौसम:** {v['pathogen_cause']}\n\n"
                    f"🌿 **जैविक व देसी रोकथाम (IPM):**\n"
                    f"• {v['immediate_cultural_action']}\n"
                    f"• {v['organic_ipm_remedy']}\n\n"
                    f"🧪 **संस्तुत रासायनिक उपचार (CIBRC अनुमोदित):**\n"
                    f"• संस्तुत दवा: **{chem_name}**\n"
                    f"• मात्रा: {chem_dose}\n\n"
                    f"{v['weather_spray_advisory']}"
                )
                if v.get("needs_symptom_clarification"):
                    qs = "\n".join([f"• {item}" for item in v.get("clarifying_questions", [])])
                    state.tool_output += f"\n\n❓ **लक्षण पुष्टिकरण प्रश्न:**\nनिदान को 100% सटीक करने हेतु कृपया पुष्टि करें:\n{qs}"
                state.follow_up_suggestions = ["छिड़काव का सबसे सही समय क्या है?", "दवा डालने के कितने दिन बाद फसल काटें?", "जैविक नीम स्प्रे का तरीका"]

            state.citations = [{
                "source": "भारतीय बागवानी अनुसंधान संस्थान (ICAR - IIHR, Bengaluru) / CIBRC",
                "authority": "ICAR",
                "title": f"{v['crop']} {v['disease_name_hindi']} प्रबंधन दिशानिर्देश",
                "citation_badge": f"[ICAR {v['crop_en']} IPM 2024]",
                "relevance_score": 0.96
            }]

        # Case 2: Weather Forecast
        elif state.intent == "WEATHER_FORECAST":
            state.add_badge("weather_tool", "✓ मौसम पूर्वानुमान मॉडल", "✓ Weather Intelligence Model")
            state.add_thought("Executing Weather Intelligence Model..." if lang == "en" else "मौसम पूर्वानुमान मॉडल निष्पादित किया गया।")
            advisories = generate_agricultural_weather_advisories(state.weather, crop, lang=lang)
            forecast = state.weather.get("forecast", [])
            forecast_lines = []
            for d in forecast[:3]:
                day_name = d.get("day", "")
                cond = d.get("condition", "")
                t_max = d.get("temp_max", "")
                t_min = d.get("temp_min", "")
                r_prob = d.get("rain_prob", 0)
                forecast_lines.append(
                    f"• **{day_name}**: {cond} | {t_min}°C - {t_max}°C | 🌧️ बारिश संभावना: {r_prob}%"
                    if lang == "hi" else
                    f"• **{day_name}**: {cond} | {t_min}°C - {t_max}°C | 🌧️ Rain Probability: {r_prob}%"
                )

            adv_text = "\n".join([f"• {a['message']}" for a in advisories])
            if lang == "en":
                state.tool_output = (
                    f"🌤️ **Agro-Meteorological Advisory for {state.location_label}:**\n\n"
                    f"• **Current Temperature:** {state.temp}°C\n"
                    f"• **Relative Humidity:** {state.humidity}%\n"
                    f"• **Wind Speed:** {state.wind_speed} km/h\n\n"
                    f"📅 **3-Day Farming Forecast:**\n" + "\n".join(forecast_lines) + "\n\n"
                    f"🚜 **Agricultural Weather Action Rules:**\n{adv_text}"
                )
                state.follow_up_suggestions = ["Can I spray pesticides today?", "Will it rain tomorrow?", "Best irrigation timing"]
            else:
                state.tool_output = (
                    f"🌤️ **{state.location_label} के लिए कृषि मौसम सलाह:**\n\n"
                    f"• **वर्तमान तापमान:** {state.temp}°C\n"
                    f"• **सापेक्ष आर्द्रता (नमी):** {state.humidity}%\n"
                    f"• **हवा की गति:** {state.wind_speed} किमी/घंटा\n\n"
                    f"📅 **आगामी 3 दिनों का कृषि पूर्वानुमान:**\n" + "\n".join(forecast_lines) + "\n\n"
                    f"🚜 **किसान भाइयों के लिए सामयिक सलाह:**\n{adv_text}"
                )
                state.follow_up_suggestions = ["क्या आज कीटनाशक छिड़काव कर सकते हैं?", "क्या कल बारिश होगी?", "सिंचाई का सही समय"]

        # Case 3: Soil Analysis
        elif state.intent == "SOIL_ANALYSIS":
            state.add_badge("soil_tool", "✓ मृदा परीक्षण विश्लेषण", "✓ Soil Health Diagnostic")
            state.add_thought("Executing Soil Diagnostic Engine..." if lang == "en" else "मृदा विश्लेषण इंजन निष्पादित किया गया।")
            metrics = extract_soil_metrics_from_text(q)
            if metrics.get("has_metrics"):
                analysis = analyze_soil_metrics(
                    n=metrics.get("nitrogen"),
                    p=metrics.get("phosphorus"),
                    k=metrics.get("potassium"),
                    ph=metrics.get("ph"),
                    oc=metrics.get("organic_carbon"),
                    crop_key=state.crop or "wheat"
                )
                state.tool_output = analysis.get("advice_english" if lang == "en" else "advice_hindi", "")
            else:
                labs = find_nearby_soil_labs(state.farmer_profile.get("district", "Lucknow"), state.farmer_profile.get("state", "Uttar Pradesh"))
                lab_lines = []
                for lab in labs[:2]:
                    lab_lines.append(f"• **{lab.get('name', '')}**: {lab.get('address', '')} (📞 {lab.get('contact', '1800-180-1551')})")
                lab_str = "\n".join(lab_lines)
                if lang == "en":
                    state.tool_output = (
                        f"🌱 **Soil Health Card Diagnostic Guide:**\n\n"
                        f"Please provide your soil test metrics (e.g. pH 7.2, N 180, P 14, K 150 kg/ha).\n\n"
                        f"🏢 **Authorized Government Soil Testing Labs in {state.location_label}:**\n{lab_str}\n\n"
                        f"💡 Soil samples should be collected in a 'V' shape up to 15 cm depth from 8-10 points across the field."
                    )
                else:
                    state.tool_output = (
                        f"🌱 **मृदा स्वास्थ्य कार्ड (Soil Health Card) मार्गदर्शिका:**\n\n"
                        f"सटीक खाद की गणना के लिए कृपया अपने मृदा परीक्षण के मान बताएं (उदा: pH 7.2, नाइट्रोजन 180, फास्फोरस 14, पोटाश 150)।\n\n"
                        f"🏢 **{state.location_label} के अधिकृत सरकारी मृदा परीक्षण केंद्र:**\n{lab_str}\n\n"
                        f"💡 खेत में 'V' आकार के 15 सेमी गहरे गड्ढे बनाकर 8-10 जगहों से मिट्टी का नमूना लें।"
                    )
            state.follow_up_suggestions = ["मिट्टी का नमूना कैसे लें?", "यूरिया की सही मात्रा क्या है?", "सरकारी मृदा कार्ड के लाभ"] if lang == "hi" else ["How to collect soil samples?", "Correct Urea dosage", "Soil Card Benefits"]

        # Case 4: Fertilizer Advisory
        elif state.intent == "FERTILIZER_ADVISORY":
            state.add_badge("fert_tool", "✓ संतुलित उर्वरक कैलकुलेटर", "✓ Balanced Fertilizer Engine")
            state.add_thought("Calculating ICAR balanced fertilizer schedule..." if lang == "en" else "ICAR संतुलित उर्वरक गणना निष्पादित की गई।")
            land_acres = float(state.farmer_profile.get("land_acres", 2.0))
            sched = calculate_fertilizer_schedule(
                crop=crop,
                rain_forecast_48h=state.rain_expected_48h,
                acres=land_acres
            )
            bags = sched.get("recommendation_bags", {})
            header = (
                f"🌾 **{sched.get('crop_en', 'Crop')} Balanced Fertilizer Schedule ({land_acres} Acres):**\n"
                f"• **Total Required:** DAP: {bags.get('dap_kg')} kg ({bags.get('dap_bags_50kg')} bags) | Urea: {bags.get('urea_kg')} kg ({bags.get('urea_bags_45kg')} bags) | MOP: {bags.get('mop_kg')} kg ({bags.get('mop_bags_50kg')} bags)\n"
                if lang == "en" else
                f"🌾 **{sched.get('crop', 'फसल')} संतुलित उर्वरक अनुशंसा ({land_acres} एकड़ खेत):**\n"
                f"• **कुल खाद:** डीएपी (DAP): {bags.get('dap_kg')} किग्रा ({bags.get('dap_bags_50kg')} बोरी) | यूरिया: {bags.get('urea_kg')} किग्रा ({bags.get('urea_bags_45kg')} बोरी) | पोटाश (MOP): {bags.get('mop_kg')} किग्रा ({bags.get('mop_bags_50kg')} बोरी)\n"
            )
            stage_lines = []
            for st in sched.get("application_schedule", []):
                st_title = st.get("stage_en" if lang == "en" else "stage")
                st_fert = st.get("fertilizer_en" if lang == "en" else "fertilizer")
                st_inst = st.get("instructions_en" if lang == "en" else "instructions")
                stage_lines.append(f"\n📅 **{st_title}:**\n  - {st_fert}\n  - *{st_inst}*")

            state.tool_output = header + "".join(stage_lines)
            if state.rain_expected_48h:
                rain_warn = (
                    "\n\n⚠️ **Weather Alert:** Rain anticipated within 48h. Do NOT top-dress Urea now to prevent leaching losses."
                    if lang == "en" else
                    "\n\n⚠️ **मौसम चेतावनी:** आगामी 48 घंटों में बारिश की संभावना है। यूरिया की टॉप ड्रेसिंग अभी न करें अन्यथा खाद बह जाएगी।"
                )
                state.tool_output += rain_warn
            state.follow_up_suggestions = ["DAP का विकल्प क्या है?", "पहली सिंचाई कब करें?", "जीवामृत बनाने की विधि"] if lang == "hi" else ["DAP alternatives", "First irrigation timing", "Jeevamrut preparation"]

        # Case 5: Crop Recommendation
        elif state.intent == "CROP_RECOMMENDATION":
            state.add_badge("crop_tool", "✓ एआई फसल संस्तुति मॉडल", "✓ AI Crop Recommender")
            state.add_thought("Executing Agro-climatic Crop Recommender..." if lang == "en" else "कृषि-जलवायु फसल संस्तुति मॉडल निष्पादित किया गया।")
            recs = crop_recommender.recommend(
                state.farmer_profile.get("soil_type", "alluvial"),
                state.temp,
                state.humidity,
                rainfall_mm=120.0,
                season="rabi" if "गेहूं" in q or "wheat" in q else "kharif",
                top_k=3
            )
            rec_blocks = []
            rec_list = recs.get("top_recommendations", []) if isinstance(recs, dict) else recs
            for r in rec_list:
                crop_name = r.get("crop_hindi" if lang == "hi" else "crop_english")
                score = r.get("suitability_score", 90)
                why = r.get("why_recommended", "")
                rf = r.get("risk_factors", [])
                risks = ", ".join(rf) if isinstance(rf, list) else str(rf)
                rec_blocks.append(
                    f"• **{crop_name}** (उपयुक्तता: {score}%):\n  - *कारण:* {why}\n  - *जोखिम:* {risks}"
                    if lang == "hi" else
                    f"• **{crop_name}** (Suitability: {score}%):\n  - *Rationale:* {why}\n  - *Risks:* {risks}"
                )
            header = f"🌾 **{state.location_label} के लिए अनुशंसित शीर्ष फसलें:**\n\n" if lang == "hi" else f"🌾 **Recommended Crops for {state.location_label}:**\n\n"
            state.tool_output = header + "\n\n".join(rec_blocks)
            state.follow_up_suggestions = ["सरसों की उन्नत किस्में", "गेहूं की बुवाई की विधि", "कम पानी वाली फसलें"] if lang == "hi" else ["Mustard varieties", "Wheat sowing method", "Low water crops"]

        # Case 6: Pest / Disease Advisory (Text)
        elif state.intent in ["PEST_CONTROL", "DISEASE_DIAGNOSIS"]:
            state.add_badge("pest_tool", "✓ पादप सुरक्षा सलाहकार", "✓ Crop Protection Specialist")
            state.add_thought("Consulting ICAR/CIBRC Pest & Disease Registry..." if lang == "en" else "ICAR/CIBRC कीट व रोग परामर्श संकलन निष्पादित।")
            advisory = get_pest_advisory(pest_or_symptom=q, crop=crop)
            chem = advisory.get("chemical_solution", {})
            ipm = advisory.get("integrated_pest_management", {})
            cultural = "\n".join([f"• {c}" for c in ipm.get("cultural_traps", [])])
            bio = "\n".join([f"• {b}" for b in ipm.get("biological_organic", [])])

            if lang == "en":
                state.tool_output = (
                    f"🐛 **Crop Protection Advisory for {advisory.get('pest_name', 'Pest/Disease')}:**\n\n"
                    f"🔍 **Symptoms:** {advisory.get('symptoms')}\n\n"
                    f"🌿 **Cultural Management & Traps:**\n{cultural}\n\n"
                    f"🧪 **Biological & Bio-pesticides:**\n{bio}\n\n"
                    f"💊 **CIBRC Approved Chemical Intervention:**\n"
                    f"• Chemical: **{chem.get('name')}**\n"
                    f"• Dosage: {chem.get('dose')}\n"
                    f"• Caution: {chem.get('cibrc_caution')}\n\n"
                    f"💡 {advisory.get('expert_recommendation')}"
                )
                state.follow_up_suggestions = ["How to spray neem oil?", "Waiting period before harvest", "Biological pheromone traps"]
            else:
                state.tool_output = (
                    f"🐛 **पादप सुरक्षा परामर्श: {advisory.get('pest_name')}**\n\n"
                    f"🔍 **पहचान व लक्षण:** {advisory.get('symptoms')}\n\n"
                    f"🌿 **एकीकृत कीट प्रबंधन (IPM) व ट्रैप:**\n{cultural}\n\n"
                    f"🧪 **जैविक उपचार:**\n{bio}\n\n"
                    f"💊 **CIBRC अनुमोदित रासायनिक उपचार:**\n"
                    f"• दवा: **{chem.get('name')}**\n"
                    f"• मात्रा: {chem.get('dose')}\n"
                    f"• सावधानी: {chem.get('cibrc_caution')}\n\n"
                    f"💡 {advisory.get('expert_recommendation')}"
                )
                state.follow_up_suggestions = ["नीम तेल का छिड़काव कैसे करें?", "छिड़काव के कितने दिन बाद फल तोड़ें?", "जैविक फेरोमोन ट्रैप"]


        # Case 7: Government Schemes
        elif state.intent == "GOVT_SCHEME":
            state.add_badge("scheme_tool", "✓ प्रत्यक्ष किसान कल्याण योजनाएं", "✓ Direct Farmer Schemes Engine")
            state.add_thought("Querying Agricultural Welfare Schemes Registry..." if lang == "en" else "किसान कल्याण योजना डेटाबेस निष्पादित।")
            matched_schemes = scheme_catalog.find_eligible_schemes(
                state=state.farmer_profile.get("state", "Uttar Pradesh"),
                land_acres=float(state.farmer_profile.get("land_acres", 2.0))
            )
            scheme_blocks = []
            for s in matched_schemes[:2]:
                scheme_blocks.append(
                    f"🏛️ **{s.get('name')}** ({s.get('ministry')}):\n"
                    f"• **उद्देश्य:** {s.get('objective')}\n"
                    f"• **लाभ:** {s.get('benefits')}\n"
                    f"• **पात्रता:** {s.get('eligibility')}\n"
                    f"• **आधिकारिक पोर्टल:** [{s.get('portal')}]({s.get('portal')})"
                    if lang == "hi" else
                    f"🏛️ **{s.get('name')}** ({s.get('ministry')}):\n"
                    f"• **Objective:** {s.get('objective')}\n"
                    f"• **Benefits:** {s.get('benefits')}\n"
                    f"• **Eligibility:** {s.get('eligibility')}\n"
                    f"• **Official Portal:** [{s.get('portal')}]({s.get('portal')})"
                )
            state.tool_output = "\n\n".join(scheme_blocks)
            state.citations = [{
                "source": "कृषि एवं किसान कल्याण मंत्रालय (Govt of India)",
                "authority": "MoAFW",
                "title": "National Agricultural Welfare Scheme Registry 2024",
                "relevance_score": 1.0,
                "citation_badge": "[MoAFW Direct Benefits]"
            }]
            state.follow_up_suggestions = ["PM किसान e-KYC कैसे करें?", "फसल बीमा का दावा कैसे करें?", "सोलर पंप सब्सिडी आवेदन"] if lang == "hi" else ["How to complete PM-KISAN e-KYC?", "How to claim crop insurance?", "Solar pump subsidy application"]

        # Case 8: General Agriculture
        else:
            state.add_badge("agri_tool", "✓ आईसीएआर कृषि ज्ञानकोष", "✓ ICAR Knowledge Base")
            state.add_thought("Querying ICAR Knowledge Base..." if lang == "en" else "ICAR ज्ञानकोष निष्पादित किया गया।")
            rag_res = agri_rag.retrieve_with_citations(q, crop_filter=crop, top_k=2)
            if rag_res.get("grounded"):
                state.tool_output = rag_res.get("context_text", "")
            else:
                state.tool_output = (
                    "🌾 **कृषि परामर्श:** आपके द्वारा पूछे गए विषय पर सामान्य कृषि संस्तुतियों के अनुसार संतुलित उर्वरक, समय पर निराई-गुड़ाई और उचित जल प्रबंधन अपनाएं।"
                    if lang == "hi" else
                    "🌾 **Agricultural Advisory:** Based on standard agronomic practices, maintain balanced fertilization, timely weed management, and appropriate irrigation schedules."
                )
            state.follow_up_suggestions = ["गेहूं में सिंचाई का समय", "जैविक खाद कैसे बनाएं", "मौसम के अनुसार फसल"] if lang == "hi" else ["Wheat irrigation timing", "How to prepare organic manure", "Seasonal crop guide"]

        return state

    def node_ground_with_rag(self, state: AgentState) -> AgentState:
        if state.completed or state.citations:
            return state

        crop_filter = state.crop
        rag_res = agri_rag.retrieve_with_citations(
            query=f"{state.raw_query} {state.crop or ''}",
            crop_filter=crop_filter,
            top_k=2
        )
        if rag_res.get("grounded"):
            state.citations = rag_res.get("citations", [])
            state.add_badge("rag", "✓ ICAR प्रामाणिक संस्तुति", "✓ ICAR Scientific Grounding")
            state.add_thought("Authoritative ICAR scientific guideline grounded." if state.detected_language == "en" else "ICAR वैज्ञानिक संस्तुति सत्यापित की गई।")

        return state

    def node_check_post_safety(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        lang = state.detected_language
        safety_audit = validate_agricultural_safety(
            response_text=state.tool_output,
            weather_rain_prob=float(state.rain_prob),
            wind_speed=float(state.wind_speed),
            lang=lang
        )
        state.final_response = safety_audit["safe_response"]
        state.completed = True
        save_chat_turn(state.session_id, state.farmer_id, state.raw_query, state.final_response, state.intent)
        return state

    def execute(self, state: AgentState) -> AgentState:
        """Executes complete Agent Graph sequentially."""
        state = self.node_initialize(state)
        state = self.node_detect_intent(state)
        state = self.node_check_pre_safety(state)
        state = self.node_vision_diagnosis(state)
        state = self.node_check_clarification(state)
        state = self.node_resolve_agro_context(state)
        state = self.node_execute_tools(state)
        state = self.node_ground_with_rag(state)
        state = self.node_check_post_safety(state)
        return state

    def execute_stream(self, state: AgentState) -> Generator[Dict[str, Any], None, AgentState]:
        """Executes Agent Graph yielding real-time events for SSE streaming."""
        state = self.node_initialize(state)
        
        state = self.node_detect_intent(state)
        yield {"type": "badge", "badge": state.status_badges[-1] if state.status_badges else None}
        if state.thought_steps:
            yield {"type": "thought", "step": state.thought_steps[-1]}
            
        if state.completed:
            yield {"type": "chunk", "text": state.final_response}
            yield {"type": "complete", "state": state.to_dict()}
            return state

        state = self.node_check_pre_safety(state)
        if state.completed:
            yield {"type": "badge", "badge": state.status_badges[-1]}
            yield {"type": "chunk", "text": state.final_response}
            yield {"type": "complete", "state": state.to_dict()}
            return state

        if state.image_bytes:
            state = self.node_vision_diagnosis(state)
            yield {"type": "badge", "badge": state.status_badges[-1] if state.status_badges else None}
            if state.completed:
                yield {"type": "chunk", "text": state.final_response}
                yield {"type": "complete", "state": state.to_dict()}
                return state

        state = self.node_check_clarification(state)
        if state.completed:
            yield {"type": "badge", "badge": state.status_badges[-1] if state.status_badges else None}
            yield {"type": "chunk", "text": state.final_response}
            yield {"type": "complete", "state": state.to_dict()}
            return state

        state = self.node_resolve_agro_context(state)
        yield {"type": "badge", "badge": state.status_badges[-1] if state.status_badges else None}

        state = self.node_execute_tools(state)
        yield {"type": "badge", "badge": state.status_badges[-1] if state.status_badges else None}

        state = self.node_ground_with_rag(state)
        if state.citations and len(state.status_badges) > 0 and state.status_badges[-1].get("step_key") == "rag":
            yield {"type": "badge", "badge": state.status_badges[-1]}

        state = self.node_check_post_safety(state)

        # Stream out response in chunks (words or sentences)
        text = state.final_response
        chunk_size = 60
        for i in range(0, len(text), chunk_size):
            yield {"type": "chunk", "text": text[i:i+chunk_size]}

        yield {"type": "complete", "state": state.to_dict()}
        return state

agent_graph = AgriculturalAgentGraph()
