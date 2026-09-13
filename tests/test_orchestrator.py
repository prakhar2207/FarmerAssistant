import pytest
from app.core.orchestrator import agent_orchestrator
from app.core.intent import detect_intent_and_slots

def test_intent_detection_hindi():
    res = detect_intent_and_slots("मेरी फसल में पत्ते पीले हो रहे हैं")
    assert res["intent"] == "DISEASE_DIAGNOSIS"
    assert res["needs_clarification"] is True
    assert res["language"] == "hi"

def test_intent_detection_english():
    res = detect_intent_and_slots("Wheat crop leaves are turning yellow")
    assert res["intent"] == "DISEASE_DIAGNOSIS"
    assert res["crop"] == "wheat"
    assert res["language"] == "en"

def test_orchestrator_fertilizer_query_hindi():
    query = "गेहूं की फसल में यूरिया और डीएपी की कितनी खाद डालें?"
    res = agent_orchestrator.process_query(query, session_id="test_sess_hi")
    assert "response" in res
    assert "डीएपी" in res["response"] or "यूरिया" in res["response"]

def test_orchestrator_fertilizer_query_english():
    query = "How much DAP and Urea fertilizer should I apply for wheat?"
    res = agent_orchestrator.process_query(query, session_id="test_sess_en", lang="en")
    assert "response" in res
    assert res["language"] == "en"
    assert "DAP" in res["response"]
    assert "Urea" in res["response"]
    assert "Schedule" in res["response"]

def test_orchestrator_clarification_flow_english():
    query = "My crop is infested with insects, what should I do?"
    res = agent_orchestrator.process_query(query, session_id="test_sess_en_clarify", lang="en")
    assert "Which crop" in res["response"]
