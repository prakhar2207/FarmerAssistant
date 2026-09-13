import pytest
from app.core.orchestrator import agent_orchestrator
from app.core.intent import detect_intent_and_slots

def test_intent_detection():
    # Crop missing, should request clarification
    res = detect_intent_and_slots("मेरी फसल में पत्ते पीले हो रहे हैं")
    assert res["intent"] == "DISEASE_DIAGNOSIS"
    assert res["needs_clarification"] is True

    # Crop present
    res2 = detect_intent_and_slots("गेहूं में पहली सिंचाई पर कौन सी खाद डालें?")
    assert res2["intent"] == "FERTILIZER_ADVISORY"
    assert res2["crop"] == "wheat"

def test_orchestrator_fertilizer_query():
    query = "गेहूं की फसल में यूरिया और डीएपी की कितनी खाद डालें?"
    res = agent_orchestrator.process_query(query, session_id="test_sess_1")
    assert "response" in res
    assert "विचार प्रक्रिया" in " ".join(res["thought_steps"]) or len(res["thought_steps"]) > 0
    assert len(res["follow_up_suggestions"]) > 0
    assert "डीएपी" in res["response"] or "यूरिया" in res["response"]

def test_orchestrator_clarification_flow():
    # Ambiguous query
    query = "फसल में कीड़ा लगा है क्या करें?"
    res = agent_orchestrator.process_query(query, session_id="test_sess_2")
    assert "किस फसल" in res["response"] or "लक्षण" in res["response"]
