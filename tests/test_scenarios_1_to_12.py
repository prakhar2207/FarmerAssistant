import io
import pytest
import numpy as np
from PIL import Image

from app.core.orchestrator import agent_orchestrator
from app.core.intent import detect_intent_and_slots
from app.core.safety import check_query_for_banned_chemicals, validate_agricultural_safety
from app.modules.disease.yolo_service import yolo_leaf_service
from app.modules.disease.detector import disease_detector
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.labs import find_nearby_soil_labs
from app.modules.crop_recommender.model import crop_recommender
from app.modules.rag.retriever import agri_rag
from app.modules.schemes.scheme_catalog import scheme_catalog

def create_synthetic_leaf(green_dominant=True, with_spots=True, non_leaf=False) -> bytes:
    """Helper to generate synthetic leaf or non-leaf test images."""
    if non_leaf:
        # Non-leaf: pure dark gray noise without chlorophyll green
        arr = np.zeros((128, 128, 3), dtype=np.uint8)
        arr[:, :] = [30, 30, 30]
    elif with_spots:
        # Diseased leaf: green leaf with distinct chlorosis halo and necrotic spots
        arr = np.zeros((128, 128, 3), dtype=np.uint8)
        arr[:, :, 1] = 165  # Green chlorophyll
        arr[:, :, 0] = 50
        arr[:, :, 2] = 40
        # Yellow chlorotic halo
        arr[25:80, 25:80, 0] = 175
        arr[25:80, 25:80, 1] = 155
        arr[25:80, 25:80, 2] = 35
        # Dark necrotic lesion center
        arr[35:60, 35:60] = [40, 40, 40]
    else:
        # Healthy green leaf
        arr = np.zeros((128, 128, 3), dtype=np.uint8)
        arr[:, :, 1] = 190
        arr[:, :, 0] = 50
        arr[:, :, 2] = 40

    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ---------------------------------------------------------
# Scenario 1: Hindi question about wheat fertilizer schedule
# ---------------------------------------------------------
def test_scenario_01_wheat_fertilizer_schedule():
    query = "गेहूं में खाद की मात्रा और डालने का समय बताओ"
    res = agent_orchestrator.process_query(query=query, lang="hi")
    assert res["intent"] == "FERTILIZER_ADVISORY"
    assert "खाद" in res["response"] or "यूरिया" in res["response"]
    assert "डीएपी" in res["response"] or "DAP" in res["response"]
    # Verify status badges present and no raw CoT exposed
    assert len(res.get("status_badges", [])) >= 2
    for b in res["status_badges"]:
        assert "✓" in b["label_hi"] or "✓" in b["label_en"] or "⚠️" in b["label_hi"] or "❓" in b["label_hi"]


# ---------------------------------------------------------
# Scenario 2: YOLO diseased tomato leaf (High confidence)
# ---------------------------------------------------------
def test_scenario_02_tomato_leaf_yolo_detection():
    img_bytes = create_synthetic_leaf(with_spots=True)
    res = yolo_leaf_service.infer(image_bytes=img_bytes, crop_hint="tomato", lang="hi")
    assert res["success"] is True
    assert res["is_leaf"] is True
    assert len(res["bounding_boxes"]) >= 1
    # Check bounding box format [x1, y1, x2, y2]
    bbox = res["bounding_boxes"][0]
    assert "x1" in bbox and "y1" in bbox and "x2" in bbox and "y2" in bbox
    assert bbox["x2"] > bbox["x1"]
    assert bbox["y2"] > bbox["y1"]
    assert res["confidence_score"] >= 75
    assert res["confidence_tier"] == "high"
    assert "झुलसा" in res["disease_name_hindi"] or "Early Blight" in res["disease_name_en"] or "Late Blight" in res["disease_name_en"]


# ---------------------------------------------------------
# Scenario 3: Combined Multimodal Query (Image + Hindi Text)
# ---------------------------------------------------------
def test_scenario_03_multimodal_image_plus_text():
    img_bytes = create_synthetic_leaf(with_spots=True)
    query = "इस बीमारी का इलाज क्या है और क्या सावधानी रखनी चाहिए?"
    res = agent_orchestrator.process_query(
        query=query,
        image_bytes=img_bytes,
        lang="hi"
    )
    assert res["vision"] is not None
    assert res["vision"]["success"] is True
    assert "पत्ती रोग विश्लेषण" in res["response"] or "निदान" in res["response"]
    # Citations grounded from RAG
    assert len(res.get("citations", [])) >= 1
    assert "ICAR" in res["citations"][0]["authority"] or "IIVR" in res["citations"][0]["source"] or "CIBRC" in res["citations"][0]["authority"]


# ---------------------------------------------------------
# Scenario 4: Request for Banned Pesticide (Safety Guardrail)
# ---------------------------------------------------------
def test_scenario_04_banned_pesticide_safety_block():
    query = "क्या मैं अपनी फसल में मोनोक्रोटोफॉस (Monocrotophos) या एंडोसल्फान का स्प्रे कर सकता हूँ?"
    res = agent_orchestrator.process_query(query=query, lang="hi")
    assert res["intent"] == "SAFETY_BLOCKED"
    assert "प्रतिबंधित" in res["response"] or "Banned" in res["response"]
    assert "CIBRC" in res["response"]
    # Check that safe alternatives are provided
    assert "इमिडाक्लोप्रिड" in res["response"] or "नीम" in res["response"] or "कोराजन" in res["response"]


# ---------------------------------------------------------
# Scenario 5: Spray query during rain forecast (Weather Guardrail)
# ---------------------------------------------------------
def test_scenario_05_spray_during_rain_forecast():
    # Test safety validation when rain probability >= 30%
    safety = validate_agricultural_safety("दवा का छिड़काव करें", weather_rain_prob=50.0, wind_speed=8.0, lang="hi")
    assert safety["is_safe"] is True
    assert "मौसम चेतावनी" in safety["safe_response"]
    assert "स्थगित" in safety["safe_response"]


# ---------------------------------------------------------
# Scenario 6: Soil Health Card analysis & KVK lab lookup
# ---------------------------------------------------------
def test_scenario_06_soil_health_card_and_kvk():
    analysis = analyze_soil_metrics(ph=8.2, oc=0.35, n=180.0, p=9.0, k=240.0, state="Uttar Pradesh")
    assert analysis["health_score"] < 75  # Deficient
    assert len(analysis["deficiencies"]) >= 2  # Low N and low P
    # Soil amendment recommendation for alkaline soil (Gypsum)
    assert any("जिप्सम" in a.get("action", "") or "क्षारीय" in a.get("action", "") or "Gypsum" in a.get("action_en", "") for a in analysis["amendments"])
    
    # Check lab finder
    labs = find_nearby_soil_labs(state="Uttar Pradesh", district="Lucknow")
    assert len(labs) >= 1
    assert any("KVK" in l["type"] or "ICAR" in l["type"] or "Government" in l["type"] for l in labs)


# ---------------------------------------------------------
# Scenario 7: Out-of-domain query deflection
# ---------------------------------------------------------
def test_scenario_07_out_of_domain_deflection():
    query = "कल भारत और ऑस्ट्रेलिया के क्रिकेट मैच का स्कोर क्या रहा?"
    res = agent_orchestrator.process_query(query=query, lang="hi")
    assert res["intent"] == "OUT_OF_DOMAIN"
    assert "केवल कृषि" in res["response"] or "कृषि सारथी" in res["response"]
    assert len(res.get("citations", [])) == 0  # Does not trigger heavy RAG


# ---------------------------------------------------------
# Scenario 8: Ambiguous query handling (Clarification Counter-Question)
# ---------------------------------------------------------
def test_scenario_08_ambiguous_query_clarification():
    query = "मेरी फसल खराब हो रही है, कोई अच्छी दवा बताओ"
    res = agent_orchestrator.process_query(query=query, session_id="session_ambiguous_test", lang="hi")
    assert any("स्पष्टीकरण" in b.get("label_hi", "") for b in res.get("status_badges", [])) or "?" in res["response"]
    assert "किस फसल" in res["response"] or "फसल का नाम" in res["response"] or "पत्ते" in res["response"]


# ---------------------------------------------------------
# Scenario 9: Medium confidence leaf image (Symptom Clarification)
# ---------------------------------------------------------
def test_scenario_09_medium_confidence_symptom_questions():
    # Mild symptoms without crop hint
    arr = np.zeros((128, 128, 3), dtype=np.uint8)
    arr[:, :, 1] = 160  # Mild green
    arr[40:60, 40:60, 0] = 120  # Mild yellowing
    arr[40:60, 40:60, 1] = 120
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    
    res = yolo_leaf_service.infer(image_bytes=buf.getvalue(), crop_hint="", lang="hi")
    assert res["success"] is True
    assert res["confidence_tier"] in ["medium", "high"]
    if res["confidence_tier"] == "medium":
        assert res["needs_symptom_clarification"] is True
        assert len(res["clarifying_questions"]) >= 1


# ---------------------------------------------------------
# Scenario 10: Low confidence / Non-leaf image rejection
# ---------------------------------------------------------
def test_scenario_10_non_leaf_image_rejection():
    non_leaf_bytes = create_synthetic_leaf(non_leaf=True)
    res = yolo_leaf_service.infer(image_bytes=non_leaf_bytes, lang="hi")
    assert res["success"] is False
    assert res["is_leaf"] is False
    assert res["confidence_tier"] == "low"
    assert "1800-180-1551" in res["helpline"] or "1800-180-1551" in res["guidance"]


# ---------------------------------------------------------
# Scenario 11: Government scheme advisory
# ---------------------------------------------------------
def test_scenario_11_government_scheme_search():
    query = "PM-KISAN सम्मान निधि योजना की पात्रता और लाभ क्या हैं?"
    schemes = scheme_catalog.search("PM-KISAN")
    assert len(schemes) >= 1
    assert "PM-KISAN" in schemes[0]["name"]
    assert "6,000" in schemes[0]["benefits"] or "6000" in schemes[0]["benefits"]
    assert "helpline" in schemes[0]


# ---------------------------------------------------------
# Scenario 12: Crop recommendation with agro-calendar
# ---------------------------------------------------------
def test_scenario_12_crop_recommendation_and_calendar():
    rec = crop_recommender.recommend(n=85, p=45, k=40, temperature=28.0, humidity=70.0, ph=6.8, rainfall=120.0, month=7)
    assert rec["success"] is True
    assert len(rec["top_recommendations"]) >= 3
    top_crop = rec["top_recommendations"][0]
    assert "suitability_score" in top_crop
    assert "sowing_months" in top_crop
    assert "water_need" in top_crop
