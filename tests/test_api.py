import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "system" in data

def test_chat_endpoint():
    payload = {
        "message": "गेहूं के प्रमुख रोग और रोकथाम के उपाय बताएं",
        "session_id": "test_session_api",
        "farmer_id": "default_farmer"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "thought_steps" in data
    assert "follow_up_suggestions" in data

def test_crop_recommend_endpoint():
    payload = {
        "n": 90.0, "p": 45.0, "k": 40.0,
        "temperature": 24.0, "humidity": 80.0,
        "ph": 6.5, "rainfall": 200.0,
        "month": 7
    }
    response = client.post("/api/crop/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["top_recommendations"]) == 3

def test_soil_analyze_endpoint():
    payload = {
        "ph": 7.4, "ec": 0.4, "oc": 0.5,
        "n": 220.0, "p": 14.0, "k": 160.0,
        "zn": 0.7, "fe": 5.0, "s": 11.0,
        "state": "Uttar Pradesh", "district": "Lucknow"
    }
    response = client.post("/api/soil/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "health_score" in data
    assert "nearby_labs" in data
    assert len(data["nearby_labs"]) > 0

def test_weather_endpoint():
    response = client.get("/api/weather?district=Lucknow")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "agricultural_advisories" in data

def test_schemes_endpoint():
    response = client.get("/api/schemes?q=kisan")
    assert response.status_code == 200
    data = response.json()
    assert "schemes" in data
    assert len(data["schemes"]) > 0
