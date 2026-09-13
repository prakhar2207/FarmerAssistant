import os
from typing import Dict, Any, List, Optional, Generator
from app.core.agent_state import AgentState
from app.core.intent import detect_intent_and_slots
from app.core.safety import validate_agricultural_safety, check_query_for_banned_chemicals
from app.core.memory import get_farmer_profile, get_recent_chat_history, save_chat_turn
from app.core.context_builder import build_agro_context
from app.core.response_planner import plan_agricultural_response
from app.core.response_generator import generate_response_text
from app.modules.weather.service import get_weather_data, resolve_location
from app.modules.disease.yolo_service import yolo_leaf_service
from app.modules.rag.retriever import agri_rag

class AgriculturalAgentGraph:
    """
    Explicit State Machine / Graph Orchestrator for KrishiSaathi.
    Orchestrates:
    1. Query Analysis & Slot Extraction
    2. Pre-execution CIBRC Chemical Safety Guardrail
    3. Multimodal YOLO Computer Vision
    4. Missing Slot Clarification Check
    5. Agro-Climatic & Weather Context Resolution
    6. Response Planning (Intent-First Domain Reasoning)
    7. Direct SME Response Generation (Zero Generic Fallback)
    8. Post-execution Safety, Weather-Spray Constraints & Disclaimers
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
        state.target_day = intent_data.get("target_day", "today")
        state.action_type = intent_data.get("action_type")
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
            f"✓ Intent: {state.intent} (Confidence: {int(state.intent_confidence*100)}%) | Crop: {state.crop or 'None'} | Target: {state.target_day}"
            if lang == "en" else
            f"✓ उद्देश्य: {state.intent} (सटीकता: {int(state.intent_confidence*100)}%) | फसल: {state.crop or 'उल्लेख नहीं'} | समय: {state.target_day}"
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
            save_chat_turn(state.session_id, state.farmer_id, state.raw_query, state.final_response, str(state.intent))

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

        return state

    def node_execute_tools(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        lang = state.detected_language
        q = state.raw_query

        # Multimodal Vision Diagnosis Case
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
            state.tools_used = ["yolo_vision", "pest_tool"]
            return state

        # Text Inquiries: Build Context & Execute Response Planner
        ctx = build_agro_context(state)
        plan = plan_agricultural_response(ctx)
        state.response_plan = plan.__dict__
        state.tools_used = plan.tools_used
        state.citations = plan.citations
        state.follow_up_suggestions = plan.follow_up_suggestions_en if lang == "en" else plan.follow_up_suggestions_hi

        # Truthful Status Badges & Thought Traces based strictly on tools_used
        badge_definitions = {
            "weather_tool": ("weather_tool", "✓ मौसम पूर्वानुमान मॉडल", "✓ Weather Intelligence Model"),
            "fert_tool": ("fert_tool", "✓ संतुलित उर्वरक कैलकुलेटर", "✓ Balanced Fertilizer Engine"),
            "pest_tool": ("pest_tool", "✓ पादप सुरक्षा सलाहकार", "✓ Crop Protection Specialist"),
            "soil_tool": ("soil_tool", "✓ मृदा परीक्षण विश्लेषण", "✓ Soil Health Diagnostic"),
            "crop_tool": ("crop_tool", "✓ एआई फसल संस्तुति मॉडल", "✓ AI Crop Recommender"),
            "scheme_tool": ("scheme_tool", "✓ प्रत्यक्ष किसान कल्याण योजनाएं", "✓ Direct Farmer Schemes Engine"),
            "icar_rag": ("rag", "✓ ICAR प्रामाणिक संस्तुति", "✓ ICAR Scientific Grounding")
        }

        for tool_key in plan.tools_used:
            if tool_key in badge_definitions:
                b_key, b_hi, b_en = badge_definitions[tool_key]
                state.add_badge(b_key, b_hi, b_en)
                state.add_thought(f"Executed tool module: {tool_key}" if lang == "en" else f"सक्रिय कृषि टूल: {b_hi}")

        # Render Authentic Agricultural SME Response
        state.tool_output = generate_response_text(plan, lang=lang)
        return state

    def node_ground_with_rag(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        # If citations already attached from response plan, add RAG badge if not already added
        if state.citations:
            if not any(b.get("step_key") == "rag" for b in state.status_badges):
                state.add_badge("rag", "✓ ICAR प्रामाणिक संस्तुति", "✓ ICAR Scientific Grounding")
            return state

        crop_filter = state.crop
        rag_res = agri_rag.retrieve_with_citations(
            query=f"{state.raw_query} {state.crop or ''}",
            crop_filter=crop_filter,
            top_k=2
        )
        if rag_res.get("grounded"):
            state.citations = rag_res.get("citations", [])
            if not any(b.get("step_key") == "rag" for b in state.status_badges):
                state.add_badge("rag", "✓ ICAR प्रामाणिक संस्तुति", "✓ ICAR Scientific Grounding")
            state.add_thought("Authoritative ICAR scientific guideline grounded." if state.detected_language == "en" else "ICAR वैज्ञानिक संस्तुति सत्यापित की गई।")

        return state

    def node_check_post_safety(self, state: AgentState) -> AgentState:
        if state.completed:
            return state

        lang = state.detected_language
        is_spray_rel = False
        if state.response_plan:
            is_spray_rel = bool(state.response_plan.get("is_spray_relevant", False))

        safety_audit = validate_agricultural_safety(
            response_text=state.tool_output,
            weather_rain_prob=float(state.rain_prob),
            wind_speed=float(state.wind_speed),
            lang=lang,
            is_spray_relevant=is_spray_rel
        )
        state.final_response = safety_audit["safe_response"]
        state.completed = True
        save_chat_turn(state.session_id, state.farmer_id, state.raw_query, state.final_response, str(state.intent))
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

        state = self.node_execute_tools(state)
        # Yield any newly added tool badges
        if len(state.status_badges) > 1:
            for b in state.status_badges[1:]:
                yield {"type": "badge", "badge": b}

        state = self.node_ground_with_rag(state)
        state = self.node_check_post_safety(state)

        # Stream out response in chunks
        text = state.final_response
        chunk_size = 60
        for i in range(0, len(text), chunk_size):
            yield {"type": "chunk", "text": text[i:i+chunk_size]}

        yield {"type": "complete", "state": state.to_dict()}
        return state

agent_graph = AgriculturalAgentGraph()
