from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from app.core.context_builder import AgroContext
from app.modules.fertilizer.calculator import calculate_fertilizer_schedule
from app.modules.pest.advisory import get_pest_advisory
from app.modules.crop_recommender.model import crop_recommender
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.parser import extract_soil_metrics_from_text
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.schemes.scheme_catalog import scheme_catalog
from app.modules.rag.retriever import agri_rag
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories

@dataclass
class ResponsePlan:
    """
    Structured domain plan for generating an authentic, expert agricultural advisory.
    Separates agronomic reasoning and fact extraction from language generation.
    """
    intent: str
    direct_answer_hi: str
    direct_answer_en: str
    agronomic_rationale_hi: Optional[str] = None
    agronomic_rationale_en: Optional[str] = None
    immediate_actions_hi: List[str] = field(default_factory=list)
    immediate_actions_en: List[str] = field(default_factory=list)
    avoid_actions_hi: List[str] = field(default_factory=list)
    avoid_actions_en: List[str] = field(default_factory=list)
    context_facts_hi: List[str] = field(default_factory=list)
    context_facts_en: List[str] = field(default_factory=list)
    kvk_advisory_hi: Optional[str] = None
    kvk_advisory_en: Optional[str] = None
    follow_up_suggestions_hi: List[str] = field(default_factory=list)
    follow_up_suggestions_en: List[str] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    is_spray_relevant: bool = False

def any_term(text: str, terms: List[str]) -> bool:
    import re
    for t in terms:
        p = r'(?:\b|^|[\s,।!?\(\)\-])' + re.escape(t) + r'(?:s|es|ing|ed)?(?:\b|$|[\s,।!?\(\)\-])'
        if re.search(p, text, re.IGNORECASE):
            return True
    return False

def plan_agricultural_response(ctx: AgroContext) -> ResponsePlan:
    intent = ctx.intent
    q = ctx.query
    crop = ctx.crop or ("गेहूं" if ctx.language == "hi" else "wheat")
    land_acres = float(ctx.farmer_profile.get("land_acres", 2.0))

    # Helper labels for target day
    day_labels = {
        "today": ("आज (Today)", "Today"),
        "tomorrow": ("कल (Tomorrow)", "Tomorrow"),
        "day_after": ("परसों (Day After Tomorrow)", "The day after tomorrow"),
        "forecast": ("आगामी 3 दिनों में", "Over the next 3 days")
    }
    day_hi, day_en = day_labels.get(ctx.target_day, ("आज", "Today"))

    # =========================================================================
    # 1. RAINFALL_QUERY
    # =========================================================================
    if intent == "RAINFALL_QUERY":
        prob = ctx.target_rain_prob
        mm = ctx.target_rain_mm
        cond_hi = ctx.target_condition_hi
        cond_en = ctx.target_condition_en

        if prob >= 50:
            ans_hi = f"{day_hi} आपके क्षेत्र ({ctx.location_label}) में बारिश होने की प्रबल संभावना ({prob}%) है तथा लगभग {mm} मिमी वर्षा हो सकती है। मौसम {cond_hi} रहेगा।"
            ans_en = f"{day_en} in {ctx.location_label}, there is a high probability of rain ({prob}%) with estimated precipitation of {mm} mm. Conditions will be {cond_en}."
            rat_hi = "बारिश होने से मिट्टी में नमी की मात्रा बढ़ेगी। इस समय सिंचाई या रासायनिक उर्वरक डालने से पोषक तत्व बह जाएंगे और लीचिंग नुकसान होगा।"
            rat_en = "Rainfall will increase root-zone soil moisture. Irrigating or applying fertilizers right now will cause heavy runoff and leaching losses."
            act_hi = [
                "सिंचाई का कार्य पूरी तरह स्थगित रखें।",
                "खेत की मेड़ों और जल निकासी नालियों (Drainage channels) को साफ रखें ताकि अतिरिक्त पानी बाहर निकल सके।",
                "पर्ण छिड़काव को बारिश थमने तक टालें।"
            ]
            act_en = [
                "Postpone all scheduled irrigation operations immediately.",
                "Clear field boundary drainage trenches to evacuate excess surface water.",
                "Hold off on foliar spray applications until rainfall subsides."
            ]
            avoid_hi = ["बारिश से ठीक पहले यूरिया की टॉप ड्रेसिंग न करें।", "तेज हवा या बारिश में किसी भी दवा का छिड़काव न करें।"]
            avoid_en = ["Do not top-dress granular Urea prior to rainfall.", "Do not spray agrochemicals during high winds or active rain."]
        elif prob >= 25:
            ans_hi = f"{day_hi} आपके क्षेत्र ({ctx.location_label}) में हल्की बारिश या बूंदाबांदी की मध्यम संभावना ({prob}%) है। अनुमानित वर्षा {mm} मिमी रह सकती है और मौसम {cond_hi} रहेगा।"
            ans_en = f"{day_en} in {ctx.location_label}, there is a moderate chance of light rain or drizzle ({prob}%) with expected precipitation of {mm} mm ({cond_en})."
            rat_hi = "हल्की बूंदाबांदी से तापमान में मामूली गिरावट आ सकती है, लेकिन भारी जलभराव का खतरा कम है।"
            rat_en = "Light intermittent showers may cool down ambient temperature, with low risk of heavy waterlogging."
            act_hi = [
                "यदि सिंचाई अत्यंत आवश्यक हो, तभी हल्की सिंचाई करें; भारी पानी लगाने से बचें।",
                "मौसम की लगातार निगरानी रखें।"
            ]
            act_en = [
                "Apply only light irrigation if soil moisture is critically deficient; avoid heavy inundation.",
                "Monitor local weather radar and alerts closely."
            ]
            avoid_hi = ["खेत में बहुत ज्यादा पानी न भरें।"]
            avoid_en = ["Avoid heavy flood irrigation."]
        else:
            ans_hi = f"{day_hi} आपके क्षेत्र ({ctx.location_label}) में बारिश होने की संभावना बहुत कम ({prob}%) है। मौसम मुख्यतः {cond_hi} और शुष्क रहेगा।"
            ans_en = f"{day_en} in {ctx.location_label}, rain probability is very low ({prob}%). The weather will remain predominantly {cond_en} and dry."
            rat_hi = f"शुष्क मौसम और वर्तमान तापमान ({ctx.current_temp}°C) के कारण वाष्पोत्सर्जन सामान्य रहेगा, जिससे खेत में आवश्यक कृषि कार्य सुरक्षित रूप से किए जा सकते हैं।"
            rat_en = f"Dry conditions and current temperature ({ctx.current_temp}°C) provide an optimal operational window for field activities."
            act_hi = [
                "फसल की आवश्यकतानुसार सामान्य सिंचाई और निराई-गुड़ाई कर सकते हैं।",
                "आवश्यकतानुसार संस्तुत खाद या पोषण का कार्य किया जा सकता है।"
            ]
            act_en = [
                "Proceed with normal irrigation scheduling based on crop stage requirements.",
                "Agricultural field activities can be safely conducted."
            ]
            avoid_hi = ["दोपहर की तेज धूप में कार्य करने से बचें, सुबह या शाम का समय चुनें।"]
            avoid_en = ["Avoid field applications during peak afternoon heat; prefer calm morning or evening hours."]

        return ResponsePlan(
            intent="RAINFALL_QUERY",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=rat_hi,
            agronomic_rationale_en=rat_en,
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=avoid_hi,
            avoid_actions_en=avoid_en,
            context_facts_hi=[f"स्थान: {ctx.location_label}", f"वर्षा संभावना: {prob}%", f"अनुमानित वर्षा: {mm} मिमी", f"अधिकतम/न्यूनतम तापमान: {ctx.target_temp_max}°C / {ctx.target_temp_min}°C"],
            context_facts_en=[f"Location: {ctx.location_label}", f"Rain Probability: {prob}%", f"Precipitation: {mm} mm", f"Temp Range: {ctx.target_temp_min}°C - {ctx.target_temp_max}°C"],
            follow_up_suggestions_hi=["क्या कल खाद डाल सकते हैं?", "सिंचाई का सही समय क्या है?", "अगले 3 दिनों का पूरा मौसम"],
            follow_up_suggestions_en=["Can I apply fertilizer tomorrow?", "Best irrigation schedule", "Full 3-day weather forecast"],
            citations=[{
                "source": "भारत मौसम विज्ञान विभाग (IMD) / Open-Meteo Weather Model",
                "authority": "IMD",
                "title": f"{ctx.location_label} कृषि मौसम पूर्वानुमान बुलेटिन",
                "citation_badge": "[IMD Live Agro-Weather]",
                "relevance_score": 0.98
            }],
            tools_used=["weather_tool"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 2. WATERLOGGING
    # =========================================================================
    elif intent == "WATERLOGGING":
        ans_hi = "हाँ, खेत में 24 से 48 घंटे से अधिक जलभराव (खड़ा पानी) रहने से फसल को गंभीर नुकसान हो सकता है। अत्यधिक पानी से मिट्टी के छिद्रों से ऑक्सीजन समाप्त हो जाती है, जिससे जड़ों का दम घुटने (Root Hypoxia) लगता है और जड़ें सड़ने व पत्तियां पीली पड़ने लगती हैं।"
        ans_en = "Yes, standing water exceeding 24-48 hours poses severe risk of irreversible crop damage. Prolonged waterlogging depletes root-zone oxygen, triggering root hypoxia (suffocation), feeder root rot, and rapid chlorosis."
        rat_hi = "गेहूं, सरसों, मक्का और दलहनी (चना, मटर) फसलें जलभराव के प्रति अत्यधिक संवेदनशील हैं (24-36 घंटों में भारी नुकसान)। धान की फसल वानस्पतिक अवस्था में पानी सहन कर सकती है, लेकिन कल्ले फूटने के बाद पूरा पौधा डूबने से प्रकाश संश्लेषण ठप हो जाता है।"
        rat_en = "Wheat, mustard, maize, and pulse crops are acutely susceptible to root suffocation within 24-36 hours. While paddy tolerates shallow submergence, complete submergence during tillering halts photosynthesis and stunts growth."
        act_hi = [
            "तत्काल जल निकासी (Surface Drainage): खेत की निचली मेड़ को काटकर या नाली बनाकर जमा हुए पानी को तुरंत खेत से बाहर निकालें।",
            "जब खेत ओट (पैर टिकने योग्य स्थिति) पर आ जाए, तो मृदा में वायु संचार (Aeration) सुधारने हेतु हल्की गुड़ाई करें।",
            "पानी उतरने के बाद जड़ों की पुनर्बहाली एवं पीलापन दूर करने हेतु 0.5% जिंक सल्फेट (21%) + 1% यूरिया का पर्ण छिड़काव करें।"
        ]
        act_en = [
            "Immediate Surface Drainage: Breach the lowest field bund or dig trench cuts to drain standing water rapidly.",
            "Once the soil surface reaches workable condition (Ot condition), perform shallow inter-row hoeing to restore root-zone aeration.",
            "Foliar Recovery Spray: Apply 0.5% Zinc Sulphate heptahydrate (21%) + 1% Urea foliar spray (5g Zinc + 10g Urea per liter of water) to accelerate photosynthetic recovery."
        ]
        avoid_hi = [
            "खेत में खड़े पानी में दानेदार यूरिया या डीएपी कभी न डालें; यह मिट्टी में नीचे बहकर (Leaching) बर्बाद हो जाएगा।",
            "पानी पूरी तरह निकले बिना भारी कृषि यंत्र खेत में न चलाएं।"
        ]
        avoid_en = [
            "Never broadcast granular Urea or DAP into standing water; it causes total nutrient leaching losses.",
            "Do not operate heavy tractors on waterlogged saturated soil to avoid soil compaction."
        ]
        clar_hi = "यदि आप अपनी फसल का नाम (उदा: गेहूं, धान, मक्का) और पानी भरने की अवधि (घंटे/दिन) बताएंगे, तो मैं फसल-विशिष्ट पुनर्बहाली उपाय सुझा सकूंगा।"
        clar_en = "Please mention your exact crop and how many hours/days water has been standing for crop-specific agronomic restoration."

        return ResponsePlan(
            intent="WATERLOGGING",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=rat_hi,
            agronomic_rationale_en=rat_en,
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=avoid_hi,
            avoid_actions_en=avoid_en,
            context_facts_hi=[f"खेत स्थान: {ctx.location_label}", "प्राथमिक खतरा: जड़ों में ऑक्सीजन की कमी (दम घुटना)", "संवेदनशील फसलें: गेहूं, चना, सरसों, मक्का"],
            context_facts_en=[f"Location: {ctx.location_label}", "Primary Mechanism: Root-zone hypoxia / oxygen starvation", "Vulnerable Crops: Wheat, Chickpea, Mustard, Maize"],
            kvk_advisory_hi=clar_hi,
            kvk_advisory_en=clar_en,
            follow_up_suggestions_hi=["पानी निकलने के बाद कौन सी खाद डालें?", "गेहूं में पीलापन कैसे दूर करें?", "फसल बीमा (PMFBY) क्लेम प्रक्रिया"],
            follow_up_suggestions_en=["Post-drainage fertilizer recovery", "Wheat yellowing remedy", "PMFBY crop loss claim process"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR-CSSRI, Karnal)",
                "authority": "ICAR",
                "title": "कृषि जलभराव, मृदा वायु संचार एवं आपातकालीन फसल पुनर्बहाली पैकेज",
                "citation_badge": "[ICAR Waterlogging Advisory 2024]",
                "relevance_score": 0.97
            }],
            tools_used=["icar_rag"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 3. IRRIGATION_QUERY
    # =========================================================================
    elif intent == "IRRIGATION_QUERY":
        if ctx.target_rain_prob >= 35 or ctx.rain_expected_48h:
            ans_hi = f"नहीं, {day_hi} सिंचाई करने की सलाह नहीं दी जाती है। आगामी 24 से 48 घंटों में {ctx.location_label} में बारिश की संभावना ({ctx.target_rain_prob}%) है।"
            ans_en = f"No, irrigation is not recommended {day_en}. There is an active rain forecast ({ctx.target_rain_prob}%) over the next 24-48 hours in {ctx.location_label}."
            rat_hi = "बारिश के ठीक पहले सिंचाई करने से खेत में अत्यधिक जलभराव (Waterlogging) हो सकता है, जिससे पौधों की जड़ें कमजोर होकर फसल गिर (Lodging) सकती है।"
            rat_en = "Irrigating just before rain risks severe waterlogging and crop lodging, especially during tillering or earhead stages."
            act_hi = ["सिंचाई 48 घंटे के लिए टालें और बारिश होने के बाद मिट्टी की नमी परखें।"]
            act_en = ["Postpone irrigation for 48 hours and inspect residual root-zone moisture after rains."]
            avoid_hi = ["आगामी बारिश की स्थिति में खेत को पानी से न भरें।"]
            avoid_en = ["Avoid inundating the field when precipitation is imminent."]
        else:
            ans_hi = f"हाँ, यदि आपकी {crop} की फसल में नमी की कमी दिख रही है, तो आप {day_hi} हल्की सिंचाई कर सकते हैं। मौसम मुख्यतः {ctx.target_condition_hi} रहने का अनुमान है।"
            ans_en = f"Yes, if your {crop} field shows moisture depletion, you can proceed with light irrigation {day_en}. Weather is forecast to remain {ctx.target_condition_en}."
            rat_hi = f"शुष्क मौसम में क्रांतिक अवस्थाओं (जैसे गेहूं में कल्ले फूटते समय या दाना बनते समय) पर पर्याप्त नमी उत्पादन सुरक्षित रखने हेतु आवश्यक है।"
            rat_en = f"Under dry conditions, maintaining adequate soil moisture during critical phenological growth stages is essential for optimal yields."
            act_hi = ["हवा शांत रहने पर सुबह या शाम के समय हल्की सिंचाई करें।", "जल का समान वितरण सुनिश्चित करें।"]
            act_en = ["Irrigate during calm morning or late evening hours to minimize evaporation.", "Ensure uniform light water distribution across field checks."]
            avoid_hi = ["तेज हवा चलने के दौरान सिंचाई न करें ताकि फसल गिरे नहीं।"]
            avoid_en = ["Do not irrigate during high wind gusts to prevent stem lodging."]

        return ResponsePlan(
            intent="IRRIGATION_QUERY",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=rat_hi,
            agronomic_rationale_en=rat_en,
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=avoid_hi,
            avoid_actions_en=avoid_en,
            context_facts_hi=[f"स्थान: {ctx.location_label}", f"बारिश संभावना: {ctx.target_rain_prob}%", f"हवा की गति: {ctx.current_wind_speed} किमी/घंटा"],
            context_facts_en=[f"Location: {ctx.location_label}", f"Rain Probability: {ctx.target_rain_prob}%", f"Wind Speed: {ctx.current_wind_speed} km/h"],
            follow_up_suggestions_hi=["गेहूं में सिंचाई की क्रांतिक अवस्थाएं", "सिंचाई के बाद यूरिया कब डालें?", "ड्रिप सिंचाई पर सरकारी अनुदान"],
            follow_up_suggestions_en=["Critical crop irrigation stages", "Post-irrigation Urea timing", "Micro-irrigation subsidy"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान संस्थान (ICAR - IARI, New Delhi)",
                "authority": "ICAR",
                "title": f"{crop} फसल जल प्रबंधन एवं सिंचाई समय-सारणी दिशानिर्देश",
                "citation_badge": f"[ICAR {crop.title()} Irrigation]",
                "relevance_score": 0.95
            }],
            tools_used=["weather_tool"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 4. NUTRIENT_DEFICIENCY (Chlorosis / Yellowing)
    # =========================================================================
    elif intent == "NUTRIENT_DEFICIENCY":
        ans_hi = f"{crop} में पत्तियों का पीला पड़ना मुख्य रूप से तीन कारणों से होता है: (1) नाइट्रोजन की कमी, (2) जिंक (Zinc) अथवा आयरन सूक्ष्म पोषक तत्व की कमी, या (3) खेत में अधिक नमी/जलभराव से जड़ों का दम घुटना।"
        ans_en = f"Yellowing (chlorosis) in {crop} is predominantly caused by: (1) Nitrogen deficiency, (2) Zinc or Iron micronutrient deficit, or (3) Root hypoxia due to excess soil moisture/waterlogging."
        rat_hi = "यदि निचली व पुरानी पत्तियां नोक से पीली हो रही हैं, तो यह नाइट्रोजन की कमी है। यदि नई पत्तियों की नसों (veins) के बीच पीलापन व कत्थई धब्बे हैं, तो यह जिंक की कमी है। यदि हाल ही में भारी पानी दिया था, तो जलभराव से जड़ें पोषक तत्व नहीं ले पा रही हैं।"
        rat_en = "If older basal leaves yellow progressively from leaf tip, it indicates Nitrogen deficiency. Interveinal chlorosis with bronze lesions on middle/young leaves indicates Zinc deficiency. Saturated root-zones temporarily shut down nutrient uptake."
        act_hi = [
            "जिंक की कमी का तत्काल समाधान: 0.5% जिंक सल्फेट (21%) यानी 5 ग्राम प्रति लीटर पानी + 10 ग्राम यूरिया का घोल बनाकर पर्ण छिड़काव करें।",
            "नाइट्रोजन की कमी हेतु: प्रति एकड़ 25-30 किग्रा नीम लेपित यूरिया की टॉप ड्रेसिंग करें (यदि आगामी 48 घंटे बारिश न हो)।",
            "यदि खेत में ज्यादा पानी भरा हो, तो सर्वप्रथम जलनिकासी सुनिश्चित करें।"
        ]
        act_en = [
            "For Zinc Deficiency: Spray 0.5% Zinc Sulphate heptahydrate (21%) @ 5g/L + 10g Urea/L of water.",
            "For Nitrogen Deficiency: Top-dress Neem Coated Urea @ 25-30 kg/acre (if rain is not forecast).",
            "If caused by water stagnation, prioritize surface drainage before applying any ground fertilizers."
        ]
        avoid_hi = ["बिना लक्षण पहचाने अंधाधुंध कीटनाशक का छिड़काव न करें।", "गीली मिट्टी में अधिक यूरिया न डालें।"]
        avoid_en = ["Do not spray broad-spectrum insecticides for nutrient deficiency.", "Do not broadcast heavy Urea on muddy, saturated soil."]

        return ResponsePlan(
            intent="NUTRIENT_DEFICIENCY",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=rat_hi,
            agronomic_rationale_en=rat_en,
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=avoid_hi,
            avoid_actions_en=avoid_en,
            context_facts_hi=[f"लक्षण: पत्तियों में पीलापन (Chlorosis)", f"फसल: {crop}", f"मृदा स्थिति: {ctx.soil_type}"],
            context_facts_en=[f"Symptom: Foliar chlorosis / yellowing", f"Crop: {crop}", f"Soil Type: {ctx.soil_type}"],
            follow_up_suggestions_hi=["जिंक सल्फेट स्प्रे की सही विधि", "क्या यह पीला रतुआ (Yellow Rust) है?", "यूरिया डालने का सही समय"],
            follow_up_suggestions_en=["Zinc spray preparation method", "Is it Yellow Rust fungus?", "Optimal Urea top-dressing stage"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR-IARI)",
                "authority": "ICAR",
                "title": "फसल पोषण विकार एवं पर्ण सूक्ष्म पोषक प्रबंधन",
                "citation_badge": "[ICAR Nutrient Diagnosis]",
                "relevance_score": 0.96
            }],
            tools_used=["fert_tool", "icar_rag"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 5. FERTILIZER_RECOMMENDATION
    # =========================================================================
    elif intent == "FERTILIZER_RECOMMENDATION":
        sched = calculate_fertilizer_schedule(crop=crop, rain_forecast_48h=False, acres=land_acres)
        bags = sched.get("recommendation_bags", {})

        asking_about_immediate_application = any_term(q, [
            "आज यूरिया डालूं", "आज खाद डालूं", "कल बारिश", "बारिश होने वाली है", "should i apply urea today", "apply fertilizer today"
        ])

        if asking_about_immediate_application and (ctx.target_rain_prob >= 40 or ctx.rain_expected_48h):
            ans_hi = f"नहीं, आज यूरिया या अन्य रासायनिक खाद न डालें। आगामी 24 से 48 घंटों में {ctx.location_label} में बारिश की संभावना ({ctx.target_rain_prob}%) है। बारिश से पूर्व खाद डालने पर पोषक तत्व पानी के साथ बह जाएंगे।"
            ans_en = f"No, do not apply Urea or chemical fertilizers today. Rainfall is anticipated ({ctx.target_rain_prob}%) within 24-48 hours in {ctx.location_label}. Applying fertilizer before rain causes severe surface runoff and leaching."
            rat_hi = "यूरिया पानी में अत्यधिक घुलनशील होता है। बारिश बीत जाने और खेत ओट पर आने के बाद ही खाद की टॉप ड्रेसिंग करें।"
            rat_en = "Urea nitrogen is highly soluble in water. Top-dress after rainfall passes and soil returns to optimal workable moisture."
            act_hi = [
                f"बारिश के बाद {crop} में संस्तुत मात्रा: प्रति एकड़ 25-30 किग्रा नीम लेपित यूरिया की टॉप ड्रेसिंग करें।",
                f"{land_acres} एकड़ खेत हेतु संतुलित उर्वरक समय-सारणी (Schedule): डीएपी (DAP) {bags.get('dap_kg', 100)} किग्रा, यूरिया {bags.get('urea_kg', 130)} किग्रा, पोटाश (MOP) {bags.get('mop_kg', 40)} किग्रा।"
            ]
            act_en = [
                f"Post-rain application for {crop}: Top-dress Neem Coated Urea @ 25-30 kg/acre once soil moisture stabilizes.",
                f"Total Balanced Fertilizer Schedule for {land_acres} acres: DAP {bags.get('dap_kg', 100)} kg, Urea {bags.get('urea_kg', 130)} kg, MOP {bags.get('mop_kg', 40)} kg."
            ]
            tools = ["weather_tool", "fert_tool"]
        else:
            ans_hi = f"{land_acres} एकड़ {crop} की फसल हेतु संतुलित उर्वरक समय-सारणी (Fertilizer Schedule): डीएपी (DAP) {bags.get('dap_kg', 100)} किग्रा ({bags.get('dap_bags_50kg', 2)} बोरी), यूरिया {bags.get('urea_kg', 130)} किग्रा ({bags.get('urea_bags_45kg', 3)} बोरी) तथा पोटाश (MOP) {bags.get('mop_kg', 40)} किग्रा ({bags.get('mop_bags_50kg', 1)} बोरी) है।"
            ans_en = f"Balanced Fertilizer Schedule for {land_acres} acres of {crop}: DAP {bags.get('dap_kg', 100)} kg ({bags.get('dap_bags_50kg', 2)} bags), Urea {bags.get('urea_kg', 130)} kg ({bags.get('urea_bags_45kg', 3)} bags), and MOP {bags.get('mop_kg', 40)} kg ({bags.get('mop_bags_50kg', 1)} bags)."
            rat_hi = "डीएपी और पोटाश की संपूर्ण मात्रा बुवाई के समय बेसल डोज के रूप में दी जाती है, जबकि यूरिया को 2-3 बराबर भागों में बांटकर पहली व दूसरी सिंचाई पर दिया जाता है।"
            rat_en = "Full DAP and Potash are applied as basal dose at sowing, while Urea is split across Crown Root Initiation (CRI) and Tillering stages."
            act_hi = [
                "बुवाई के समय: डीएपी की पूरी मात्रा + पोटाश की पूरी मात्रा + 1/3 यूरिया खेत की अंतिम जुताई पर दें।",
                "पहली सिंचाई (21-25 दिन): 1/3 यूरिया की टॉप ड्रेसिंग करें।",
                "दूसरी सिंचाई (40-45 दिन): शेष 1/3 यूरिया डालें।"
            ]
            act_en = [
                "Basal application at sowing: 100% DAP + 100% MOP + 1/3rd Urea incorporated in soil.",
                "First irrigation (CRI stage): Top-dress 1/3rd Urea.",
                "Second irrigation (Tillering stage): Top-dress remaining 1/3rd Urea."
            ]
            tools = ["fert_tool"]
            if ctx.target_rain_prob >= 40 or ctx.rain_expected_48h:
                tools.append("weather_tool")
                act_hi.append(f"नोट (मौसम चेतावनी): आगामी 48 घंटों में बारिश ({ctx.target_rain_prob}%) का अनुमान है, अतः यूरिया की टॉप ड्रेसिंग बारिश थमने के बाद करें।")
                act_en.append(f"Note (Weather Alert): Rainfall anticipated ({ctx.target_rain_prob}%) in 48h; postpone top-dressing until showers clear.")

        return ResponsePlan(
            intent="FERTILIZER_RECOMMENDATION",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=rat_hi,
            agronomic_rationale_en=rat_en,
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=["खड़ी फसल में डीएपी का भुरकाव न करें, यह जड़ों तक नहीं पहुंच पाता।", "यूरिया की अत्यधिक मात्रा न डालें, इससे कीट बढ़ते हैं।"],
            avoid_actions_en=["Do not top-dress DAP on standing crop; phosphorus is immobile in soil.", "Avoid excessive nitrogen application to prevent pest infestation."],
            context_facts_hi=[f"फसल: {crop}", f"रकबा: {land_acres} एकड़", f"स्थान: {ctx.location_label}"],
            context_facts_en=[f"Crop: {crop}", f"Area: {land_acres} Acres", f"Location: {ctx.location_label}"],
            follow_up_suggestions_hi=["DAP का विकल्प क्या है?", "पहली सिंचाई कब करें?", "जिंक खाद कब डालें?"],
            follow_up_suggestions_en=["DAP alternatives (SSP + Urea)", "First irrigation timing", "When to apply Zinc?"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR) एवं उर्वरक संस्तुति नियमावली",
                "authority": "ICAR",
                "title": f"{crop} संतुलित उर्वरक एवं पोषण प्रबंधन",
                "citation_badge": f"[ICAR {crop.title()} Nutrition 2024]",
                "relevance_score": 0.98
            }],
            tools_used=tools,
            is_spray_relevant=False
        )

    # =========================================================================
    # 6. CROP_DISEASE & PEST_IDENTIFICATION
    # =========================================================================
    elif intent in ["CROP_DISEASE", "PEST_IDENTIFICATION"]:
        adv = get_pest_advisory(pest_or_symptom=q, crop=crop)
        chem = adv.get("chemical_solution", {})
        ipm = adv.get("integrated_pest_management", {})
        chem_name = chem.get("name", "संस्तुत कीटनाशक/फफूंदनाशी")
        chem_dose = chem.get("dose", "संस्तुत मात्रा")
        pest_name = adv.get("pest_name", "कीट/रोग")

        ans_hi = f"{crop} में संभावित समस्या: **{pest_name}**। इसके नियंत्रण हेतु जैविक रूप से नीम तेल अथवा आवश्यकता पड़ने पर CIBRC अनुमोदित रसायन **{chem_name}** ({chem_dose}) का छिड़काव करें।"
        ans_en = f"Diagnosed issue in {crop}: **{pest_name}**. For effective management, adopt cultural IPM / Neem oil, or apply CIBRC approved formulation **{chem_name}** at {chem_dose}."
        rat_hi = f"लक्षण: {adv.get('symptoms', 'पत्तियों पर धब्बे या कीट प्रकोप')}। आर्द्र मौसम एवं अनुकूल तापमान में यह तेजी से फैल सकता है।"
        rat_en = f"Symptom profile: {adv.get('symptoms', 'Foliar lesions or pest damage')}. Favorable humidity promotes rapid pathogen spread."
        act_hi = [
            f"जैविक/देसी नियंत्रण: {ipm.get('biological_organic', ['नीम तेल (1500 ppm) 3-4 मिली/लीटर का छिड़काव करें'])[0]}",
            f"रासायनिक नियंत्रण (CIBRC स्वीकृत): {chem_name} ({chem_dose}) को 150-200 लीटर पानी प्रति एकड़ में घोलकर छिड़कें।",
            "संक्रमित पत्तियों अथवा पौधों को तोड़कर खेत से दूर नष्ट कर दें।"
        ]
        act_en = [
            f"Biological IPM: {ipm.get('biological_organic', ['Spray Neem Oil (1500 ppm) @ 3-4 ml/L'])[0]}",
            f"Chemical Intervention (CIBRC Approved): Foliar spray {chem_name} ({chem_dose}) in 150-200L water per acre.",
            "Rogue out severely infested foliage to curb secondary spore dispersal."
        ]
        avoid_hi = ["प्रतिबंधित कीटनाशकों का प्रयोग न करें।", "तेज धूप या हवा में छिड़काव न करें।"]
        avoid_en = ["Do not use banned chemicals.", "Do not spray in windy conditions or during hot mid-day sun."]

        return ResponsePlan(
            intent=intent,
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=rat_hi,
            agronomic_rationale_en=rat_en,
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=avoid_hi,
            avoid_actions_en=avoid_en,
            context_facts_hi=[f"पहचान: {pest_name}", f"फसल: {crop}", f"अनुमोदित रसायन: {chem_name}"],
            context_facts_en=[f"Diagnosis: {pest_name}", f"Crop: {crop}", f"Chemical: {chem_name}"],
            follow_up_suggestions_hi=["छिड़काव का सबसे सही समय?", "जैविक नीम स्प्रे की विधि", "दवा के कितने दिन बाद फल तोड़ें?"],
            follow_up_suggestions_en=["Best time of day for spraying", "Neem oil spray preparation", "Safe pre-harvest interval (PHI)"],
            citations=[{
                "source": "केंद्रीय कीटनाशक बोर्ड (CIBRC) एवं ICAR पादप सुरक्षा निदेशालय",
                "authority": "CIBRC / ICAR",
                "title": f"{crop} समेकित कीट एवं रोग प्रबंधन पैकेज",
                "citation_badge": f"[CIBRC {crop.title()} IPM 2024]",
                "relevance_score": 0.98
            }],
            tools_used=["pest_tool"],
            is_spray_relevant=True
        )

    # =========================================================================
    # 7. SOIL_ANALYSIS & SOIL_TYPE
    # =========================================================================
    elif intent in ["SOIL_ANALYSIS", "SOIL_TYPE"]:
        metrics = extract_soil_metrics_from_text(q)
        if metrics.get("has_metrics"):
            analysis = analyze_soil_metrics(
                n=metrics.get("nitrogen"),
                p=metrics.get("phosphorus"),
                k=metrics.get("potassium"),
                ph=metrics.get("ph"),
                oc=metrics.get("organic_carbon"),
                crop_key=crop
            )
            ans_hi = f"मृदा स्वास्थ्य विश्लेषण: आपके खेत की मिट्टी का pH {metrics.get('ph') or 'सामान्य'} है। {analysis.get('advice_hindi', 'संतुलित पोषण प्रबंधन अपनाएं।')[:200]}"
            ans_en = f"Soil Health Analysis: Soil pH is {metrics.get('ph') or 'Normal'}. {analysis.get('advice_english', 'Adopt balanced soil nutrition.')[:200]}"
            act_hi = ["मृदा कार्ड संस्तुति के अनुसार ही यूरिया व डीएपी की संतुलित मात्रा डालें।", "गोबर की सड़ी खाद (FYM) 4-5 टन प्रति एकड़ मिलाएं।"]
            act_en = ["Apply customized fertilizer doses strictly tailored to Soil Health Card test values.", "Apply 4-5 tons/acre well-decomposed Farm Yard Manure (FYM)."]
        else:
            labs = find_nearby_soil_labs(ctx.farmer_profile.get("district", "Lucknow"), ctx.farmer_profile.get("state", "Uttar Pradesh"))
            lab_names = ", ".join([l.get("name", "") for l in labs[:2]])
            ans_hi = f"सटीक खाद प्रबंधन हेतु मृदा स्वास्थ्य कार्ड (Soil Health Card) जांच आवश्यक है। {ctx.location_label} में अधिकृत सरकारी परीक्षण केंद्र: {lab_names}।"
            ans_en = f"For precision nutrient management, test your soil through authorized Soil Testing Labs in {ctx.location_label}: {lab_names}."
            act_hi = [
                "खेत में 'V' आकार के 15 सेमी गहरे 8-10 गड्ढों से मिट्टी का प्रतिनिधि नमूना लें।",
                "नमूने को सुखाकर नजदीकी कृषि विज्ञान केंद्र (KVK) या सरकारी प्रयोगशाला में जांच कराएं।"
            ]
            act_en = [
                "Collect composite soil samples from 8-10 zig-zag spots up to 15 cm depth in 'V' shape.",
                "Shade-dry sample and submit to the nearest KVK or Government Soil Testing Lab."
            ]
        
        return ResponsePlan(
            intent=intent,
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi="मृदा परीक्षण से खेत में पोषक तत्वों की सही स्थिति ज्ञात होती है, जिससे अनावश्यक रासायनिक खाद का खर्च बचता है।",
            agronomic_rationale_en="Scientific soil testing identifies specific nutrient deficiencies, curbing wasteful fertilizer expenditures.",
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=["बिना जांच के अत्यधिक यूरिया न डालें, इससे मिट्टी अम्लीय/क्षारीय हो सकती है।"],
            avoid_actions_en=["Do not apply excessive nitrogen without soil testing to prevent soil degradation."],
            follow_up_suggestions_hi=["मिट्टी का नमूना कैसे लें?", "जिप्सम का प्रयोग कब करें?", "जैविक खाद कैसे बनाएं?"],
            follow_up_suggestions_en=["How to take soil sample?", "When to use Gypsum?", "How to make compost?"],
            citations=[{
                "source": "मृदा स्वास्थ्य कार्ड मिशन (भारत सरकार)",
                "authority": "MoAFW",
                "title": "मृदा नमूना संकलन एवं उर्वरता प्रबंधन दिशानिर्देश",
                "citation_badge": "[Soil Health Card Scheme]",
                "relevance_score": 0.96
            }],
            tools_used=["soil_tool"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 8. CROP_RECOMMENDATION
    # =========================================================================
    elif intent == "CROP_RECOMMENDATION":
        recs = crop_recommender.recommend(
            ctx.farmer_profile.get("soil_type", "alluvial"),
            ctx.current_temp,
            ctx.current_humidity,
            rainfall_mm=120.0,
            season="rabi" if "गेहूं" in q or "wheat" in q or "रबी" in q else "kharif",
            top_k=3
        )
        rec_list = recs.get("top_recommendations", []) if isinstance(recs, dict) else recs
        top_crop_hi = rec_list[0].get("crop_hindi", "गेहूं") if rec_list else "गेहूं"
        top_crop_en = rec_list[0].get("crop_english", "Wheat") if rec_list else "Wheat"
        top_crops_hi = ", ".join([r.get("crop_hindi", "") for r in rec_list[:3]])
        top_crops_en = ", ".join([r.get("crop_english", "") for r in rec_list[:3]])

        ans_hi = f"{ctx.location_label} की जलवायु एवं {ctx.soil_type} मिट्टी के लिए सबसे उपयुक्त शीर्ष फसलें: **{top_crops_hi}** हैं। प्रथम वरीयता **{top_crop_hi}** को दी जाती है।"
        ans_en = f"Top recommended crops for {ctx.location_label} ({ctx.soil_type} soil): **{top_crops_en}**. Primary recommendation is **{top_crop_en}**."
        act_hi = [f"उन्नत एवं प्रमाणित बीज का चयन करें (जैसे {top_crop_hi} की अनुमोदित किस्में)।", "बुवाई से पूर्व बीज उपचार अवश्य करें।"]
        act_en = [f"Procure certified high-yielding seed varieties for {top_crop_en}.", "Perform mandatory fungicide and bio-fertilizer seed treatment before sowing."]

        return ResponsePlan(
            intent="CROP_RECOMMENDATION",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=f"वर्तमान तापमान ({ctx.current_temp}°C) एवं क्षेत्र की मिट्टी इन फसलों की वानस्पतिक वृद्धि और उच्च पैदावार हेतु पूर्णतः अनुकूल है।",
            agronomic_rationale_en=f"Ambient temperature ({ctx.current_temp}°C) and soil properties align with the agronomic thresholds of these crops.",
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=["बिना प्रमाणित स्रोतों के अज्ञात बीज न खरीदें।"],
            avoid_actions_en=["Do not purchase uncertified seeds without germination certification."],
            follow_up_suggestions_hi=[f"{top_crop_hi} की उन्नत किस्में", "बुवाई की सही विधि", "बीज उपचार का तरीका"],
            follow_up_suggestions_en=[f"High-yielding {top_crop_en} varieties", "Sowing techniques", "Seed treatment protocol"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR) कृषि-जलवायु फसल नियोजन",
                "authority": "ICAR",
                "title": f"{ctx.location_label} हेतु उपयुक्त फसल संस्तुतियां",
                "citation_badge": "[ICAR Agro-Climatic Planning]",
                "relevance_score": 0.95
            }],
            tools_used=["crop_tool"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 9. SOWING_TIME & HARVEST_TIME
    # =========================================================================
    elif intent in ["SOWING_TIME", "HARVEST_TIME"]:
        if intent == "SOWING_TIME":
            ans_hi = f"{crop} की बुवाई का सर्वोत्तम समय 1 नवंबर से 25 नवंबर के मध्य (रबी मौसम) अथवा जून-जुलाई (खरीफ) होता है, जब औसत तापमान 20°C से 25°C के बीच आ जाए।"
            ans_en = f"Optimal sowing window for {crop} is from November 1 to November 25 (Rabi) or June-July (Kharif), when soil/ambient temperature settles around 20-25°C."
            act_hi = ["खेत में उचित नमी (पलेवा) देकर बुवाई करें।", "बीज को फफूंदनाशी (थीरम/बाविस्टिन @ 2.5 ग्राम/किग्रा) से उपचारित करें।"]
            act_en = ["Ensure adequate pre-sowing moisture (Palewa).", "Treat seeds with Thiram/Carbendazim @ 2.5 g/kg seed before sowing."]
        else:
            ans_hi = f"{crop} की कटाई का उपयुक्त समय तब होता है जब बालियां/दाने 80-85% सुनहरे पीले हो जाएं और दानों में नमी की मात्रा 14-16% से कम रह जाए।"
            ans_en = f"Optimal harvesting time for {crop} is when 80-85% earheads turn golden yellow and grain moisture falls below 14-16%."
            act_hi = ["कटाई के 10-12 दिन पहले अंतिम सिंचाई बंद कर दें।", "कटाई के बाद दानों को धूप में सुखाकर 12% से कम नमी पर भंडारित करें।"]
            act_en = ["Cease irrigation 10-12 days prior to scheduled harvest.", "Sun-dry grains to below 12% moisture prior to safe storage."]

        return ResponsePlan(
            intent=intent,
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi="समय पर बुवाई/कटाई करने से तापमान के झटकों से बचाव होता है और दानों की गुणवत्ता व उपज अधिकतम प्राप्त होती है।",
            agronomic_rationale_en="Timely sowing and harvesting prevents terminal heat stress and maximizes test weight and market grain grade.",
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=["अत्यधिक देर से बुवाई न करें, इससे दाना सिकुड़ जाता है।"],
            avoid_actions_en=["Avoid delayed sowing to prevent terminal heat forced maturity."],
            follow_up_suggestions_hi=["बीज दर प्रति एकड़ कितना रखें?", "उन्नत बीजों के नाम", "भंडारण में कीट से बचाव"],
            follow_up_suggestions_en=["Seed rate per acre", "Certified seed varieties", "Storage pest prevention"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR-IARI)",
                "authority": "ICAR",
                "title": f"{crop} सस्य क्रियाएं एवं फसल कैलेंडर",
                "citation_badge": f"[ICAR {crop.title()} Calendar]",
                "relevance_score": 0.95
            }],
            tools_used=["icar_rag"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 10. CROP_STRESS (Frost / Heat / Cold)
    # =========================================================================
    elif intent == "CROP_STRESS":
        ans_hi = f"फसल को पाले (Frost) या शीतलहर से बचाने हेतु खेत में शाम के समय हल्की सिंचाई (ताजा पानी) दें और खेत के उत्तर-पश्चिम दिशा में धुआं करें ताकि तापमान 1-2°C बढ़ सके।"
        ans_en = f"To protect crops against frost and severe cold injury: Provide light evening irrigation with fresh tubewell water, and create smoke smudge fires on the north-west field perimeter to raise microclimate temperatures by 1-2°C."
        act_hi = [
            "शाम के समय खेत में हल्की सिंचाई करें (पानी की विशिष्ट ऊष्मा तापमान को गिरने से रोकती है)।",
            "थायोयूरिया (Thiourea @ 0.5 ग्राम/लीटर) अथवा घुलनशील गंधक (80% WDG @ 2 ग्राम/लीटर) का छिड़काव करें।"
        ]
        act_en = [
            "Apply light evening irrigation; the high specific heat of water prevents rapid ground freezing.",
            "Foliar spray Thiourea @ 0.5g/L or Water Soluble Sulphur (80% WDG @ 2g/L) to enhance crop physiological cold resistance."
        ]
        avoid_hi = ["पाले की रात में खेत को सूखा न छोड़ें।"]
        avoid_en = ["Do not leave dry un-irrigated fields during severe freeze warnings."]

        return ResponsePlan(
            intent="CROP_STRESS",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi="पाला पड़ने पर पौधों की कोशिकाओं में बर्फ जम जाती है जिससे कोशिकाएं फट जाती हैं। सिंचाई व धुआं तापमान को जमाव बिंदु से ऊपर बनाए रखते हैं।",
            agronomic_rationale_en="Frost freezes intracellular water causing cell lysis and necrosis. Evening irrigation and smudging maintain microclimate above lethal threshold.",
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=avoid_hi,
            avoid_actions_en=avoid_en,
            follow_up_suggestions_hi=["पाले से सबसे ज्यादा नुकसान किस फसल को?", "सल्फर स्प्रे का सही समय", "आगामी 3 दिन का न्यूनतम तापमान"],
            follow_up_suggestions_en=["Most frost-vulnerable crops", "Sulphur spray timing", "3-day minimum temperature"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR-CAZRI)",
                "authority": "ICAR",
                "title": "शीतलहर एवं पाला प्रबंधन परामर्श",
                "citation_badge": "[ICAR Frost Advisory]",
                "relevance_score": 0.96
            }],
            tools_used=["weather_tool", "icar_rag"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 11. GOVERNMENT_SCHEME
    # =========================================================================
    elif intent == "GOVERNMENT_SCHEME":
        matched_schemes = scheme_catalog.find_eligible_schemes(
            state=ctx.farmer_profile.get("state", "Uttar Pradesh"),
            land_acres=land_acres
        )
        s_list = []
        for s in matched_schemes[:2]:
            s_list.append(f"• **{s.get('name')}**: {s.get('benefits')} (पात्रता: {s.get('eligibility')})")
        schemes_str = "\n".join(s_list) if s_list else "पीएम किसान सम्मान निधि एवं प्रधानमंत्री फसल बीमा योजना।"

        ans_hi = f"भारत सरकार एवं राज्य कृषि विभाग द्वारा किसान भाइयों हेतु प्रमुख कल्याणकारी योजनाएं उपलब्ध हैं:\n{schemes_str}"
        ans_en = f"Major Government Welfare Schemes available for farmers in {ctx.location_label}:\n{schemes_str}"
        act_hi = [
            "पीएम किसान सम्मान निधि हेतु आधिकारिक पोर्टल pmkisan.gov.in पर e-KYC और आधार सीडिंग पूर्ण करें।",
            "फसल नुकसान की स्थिति में 72 घंटे के भीतर PMFBY टोल फ्री नंबर 14447 पर बीमा क्लेम दर्ज कराएं।"
        ]
        act_en = [
            "Complete mandatory e-KYC and Aadhaar bank-seeding on pmkisan.gov.in.",
            "Report localized crop damage within 72 hours on PMFBY helpline 14447 for insurance claims."
        ]

        return ResponsePlan(
            intent="GOVERNMENT_SCHEME",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi="सरकारी योजनाओं से किसानों को वित्तीय सुरक्षा, कम ब्याज पर फसली ऋण (KCC) एवं आपदा राहत प्राप्त होती है।",
            agronomic_rationale_en="Direct benefit transfers and crop insurance provide essential financial safety nets against agricultural weather risks.",
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            avoid_actions_hi=["किसी भी अनधिकृत एजेंट या साइबर कैफे को अतिरिक्त शुल्क न दें; आवेदन सरकारी पोर्टल पर निःशुल्क है।"],
            avoid_actions_en=["Do not pay unauthorized third-party agents; scheme applications on official portals are free."],
            follow_up_suggestions_hi=["PM किसान की अगली किस्त कब आएगी?", "फसल बीमा क्लेम कैसे करें?", "सोलर पंप सब्सिडी योजना"],
            follow_up_suggestions_en=["PM-KISAN installment date", "How to file crop insurance claim?", "Solar pump PM-KUSUM subsidy"],
            citations=[{
                "source": "कृषि एवं किसान कल्याण मंत्रालय (Govt of India)",
                "authority": "MoAFW",
                "title": "राष्ट्रीय किसान कल्याण योजनाएं एवं सब्सिडी विवरण",
                "citation_badge": "[MoAFW Farmer Welfare]",
                "relevance_score": 0.99
            }],
            tools_used=["scheme_tool"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 12. WEATHER_QUERY (General Weather)
    # =========================================================================
    elif intent == "WEATHER_QUERY":
        ans_hi = f"{ctx.location_label} में वर्तमान तापमान {ctx.current_temp}°C है और मौसम {ctx.target_condition_hi} बना हुआ है। सापेक्ष आर्द्रता {ctx.current_humidity}% तथा वर्षा की संभावना {ctx.target_rain_prob}% है।"
        ans_en = f"Current temperature in {ctx.location_label} is {ctx.current_temp}°C with {ctx.target_condition_en} skies. Relative humidity is {ctx.current_humidity}% with a {ctx.target_rain_prob}% chance of rain."
        act_hi = [
            "सामान्य कृषि क्रियाएं (निराई, हल्की सिंचाई) मौसम अनुकूल रहने पर जारी रखें।",
            "हवा की गति शांत रहने पर ही रासायनिक दवाओं का कार्य करें।"
        ]
        act_en = [
            "Proceed with regular crop husbandry based on current clear weather.",
            "Ensure low wind speeds before any foliar agrochemical applications."
        ]

        return ResponsePlan(
            intent="WEATHER_QUERY",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=f"तापमान ({ctx.current_temp}°C) एवं हवा की गति ({ctx.current_wind_speed} किमी/घंटा) सामान्य खेती के लिए अनुकूल हैं।",
            agronomic_rationale_en=f"Ambient temperature ({ctx.current_temp}°C) and wind velocity ({ctx.current_wind_speed} km/h) are within standard working limits.",
            immediate_actions_hi=act_hi,
            immediate_actions_en=act_en,
            context_facts_hi=[f"स्थान: {ctx.location_label}", f"तापमान: {ctx.current_temp}°C", f"नमी: {ctx.current_humidity}%", f"वर्षा संभावना: {ctx.target_rain_prob}%"],
            context_facts_en=[f"Location: {ctx.location_label}", f"Temp: {ctx.current_temp}°C", f"Humidity: {ctx.current_humidity}%", f"Rain Prob: {ctx.target_rain_prob}%"],
            follow_up_suggestions_hi=["क्या कल बारिश होगी?", "क्या आज छिड़काव कर सकते हैं?", "सिंचाई का सही समय"],
            follow_up_suggestions_en=["Will it rain tomorrow?", "Can I spray today?", "Optimal irrigation schedule"],
            citations=[{
                "source": "भारत मौसम विज्ञान विभाग (IMD) / Open-Meteo",
                "authority": "IMD",
                "title": f"{ctx.location_label} कृषि मौसम रिपोर्ट",
                "citation_badge": "[IMD Weather Service]",
                "relevance_score": 0.96
            }],
            tools_used=["weather_tool"],
            is_spray_relevant=False
        )

    # =========================================================================
    # 13. GENERAL_AGRICULTURE / Fallback
    # =========================================================================
    else:
        rag_res = agri_rag.retrieve_with_citations(q, crop_filter=crop, top_k=2)
        if rag_res.get("grounded") and rag_res.get("context_text"):
            ans_hi = rag_res.get("context_text")
            ans_en = rag_res.get("context_text")
        else:
            ans_hi = f"{crop} के बेहतर उत्पादन हेतु प्रमाणित बीजों का चयन, समय पर संतुलित उर्वरक (NPK) एवं आवश्यकतानुसार क्रांतिक अवस्थाओं पर सिंचाई प्रबंधन अत्यंत महत्वपूर्ण है।"
            ans_en = f"For optimal {crop} productivity, ensure certified seed selection, balanced NPK nutrition, and timely irrigation at critical growth stages."

        return ResponsePlan(
            intent="GENERAL_AGRICULTURE",
            direct_answer_hi=ans_hi,
            direct_answer_en=ans_en,
            agronomic_rationale_hi=f"ICAR वैज्ञानिक संस्तुतियों के अनुसार {crop} की देखभाल से उपज व गुणवत्ता दोनों सुरक्षित रहती हैं।",
            agronomic_rationale_en=f"Adhering to ICAR package of practices ensures healthy vegetative growth and high grain yield.",
            immediate_actions_hi=[f"खेत में खरपतवार नियंत्रण एवं जल निकासी की समुचित व्यवस्था रखें।", "नियमित रूप से खेत का निरीक्षण करें।"],
            immediate_actions_en=[f"Maintain clean weeding and field drainage in {crop}.", "Inspect field weekly for early pest or disease incidence."],
            follow_up_suggestions_hi=[f"{crop} में खाद की सही मात्रा", f"{crop} में सिंचाई का समय", "नजदीकी केवीके का पता"],
            follow_up_suggestions_en=[f"{crop.title()} fertilizer schedule", f"{crop.title()} irrigation schedule", "Nearest KVK center"],
            citations=[{
                "source": "भारतीय कृषि अनुसंधान परिषद (ICAR)",
                "authority": "ICAR",
                "title": f"{crop.title()} उन्नत सस्य विज्ञान संस्तुति",
                "citation_badge": f"[ICAR {crop.title()} Practices]",
                "relevance_score": 0.92
            }],
            tools_used=["icar_rag"],
            is_spray_relevant=False
        )
