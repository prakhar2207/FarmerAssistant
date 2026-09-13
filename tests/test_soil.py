import pytest
from app.modules.soil.analyzer import analyze_soil_metrics
from app.modules.soil.labs import find_nearby_soil_labs

def test_soil_analysis_acidic():
    # Acidic soil test
    res = analyze_soil_metrics(ph=5.2, oc=0.35, n=190.0, p=7.0, k=90.0)
    assert res["health_score"] < 70
    assert "अम्लीय" in res["parameters"]["pH"]["status"]
    # Lime amendment should be recommended
    actions = [a["action"] for a in res["amendments"]]
    assert any("चूना" in a for a in actions)

def test_soil_analysis_alkaline():
    # Alkaline soil test
    res = analyze_soil_metrics(ph=8.6, oc=0.55, n=310.0, p=18.0, k=210.0)
    assert "क्षारीय" in res["parameters"]["pH"]["status"]
    # Gypsum amendment should be recommended
    actions = [a["action"] for a in res["amendments"]]
    assert any("जिप्सम" in a for a in actions)

def test_nearby_labs_search():
    labs = find_nearby_soil_labs(state="Uttar Pradesh", district="Lucknow")
    assert len(labs) > 0
    assert any("Lucknow" in l["district"] or "ICAR" in l["name"] for l in labs)
