import pytest
from app.core.safety import validate_agricultural_safety

def test_safety_banned_chemical():
    sample_text = "कीट को मारने के लिए Endosulfan का 2 मिली प्रति लीटर स्प्रे करें।"
    res = validate_agricultural_safety(sample_text)
    assert res["is_safe"] is False
    assert "endosulfan" in res["flagged_chemicals"]
    assert "प्रतिबंधित रसायन" in res["safe_response"]

def test_safety_weather_spray_warning():
    sample_text = "फसल पर यूरिया का पर्ण छिड़काव करें।"
    res = validate_agricultural_safety(sample_text, weather_rain_prob=50.0)
    assert "बारिश की संभावना" in res["safe_response"]
