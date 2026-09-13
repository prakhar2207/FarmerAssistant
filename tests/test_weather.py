import pytest
from app.modules.weather.service import resolve_location, get_weather_data
from app.modules.weather.agri_rules import generate_agricultural_weather_advisories

def test_resolve_location():
    lat, lon, label = resolve_location("lucknow")
    assert "Lucknow" in label
    assert abs(lat - 26.8467) < 0.01

def test_weather_data_retrieval():
    data = get_weather_data(latitude=26.8467, longitude=80.9462, location_name="Lucknow")
    assert data["success"] is True
    assert "current" in data
    assert "temperature" in data["current"]
    assert "humidity" in data["current"]
    assert len(data["forecast"]) >= 3

def test_agri_weather_advisories():
    mock_weather = {
        "current": {"temperature": 25.0, "humidity": 85, "wind_speed": 18.0},
        "forecast": [
            {"date": "Day 1", "rain_prob": 65, "rain_sum_mm": 12.0},
            {"date": "Day 2", "rain_prob": 40, "rain_sum_mm": 5.0}
        ]
    }
    advisories = generate_agricultural_weather_advisories(mock_weather)
    titles = [a["title"] for a in advisories]
    
    # Should flag spray postponement due to rain and high wind
    assert any("स्थगित" in t for t in titles)
    # Should flag fungal disease risk due to high humidity (85%)
    assert any("फफूंद" in t for t in titles)
