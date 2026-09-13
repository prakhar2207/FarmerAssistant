import pytest
from app.modules.crop_recommender.model import crop_recommender

def test_crop_recommendation_rice():
    # High rainfall, high humidity, warm temp, suitable for rice
    res = crop_recommender.recommend(n=80, p=45, k=40, temperature=24.0, humidity=85.0, ph=6.2, rainfall=220.0, month=7)
    assert res["success"] is True
    assert len(res["top_recommendations"]) == 3
    top_crop = res["top_recommendations"][0]["crop_key"]
    assert top_crop in ["rice", "jute", "banana"]

def test_crop_recommendation_wheat():
    # Moderate temp, moderate rainfall, suitable for wheat / chickpea
    res = crop_recommender.recommend(n=100, p=50, k=35, temperature=18.0, humidity=60.0, ph=6.8, rainfall=70.0, month=11)
    assert res["success"] is True
    assert len(res["top_recommendations"]) == 3
    top_crops = [c["crop_key"] for c in res["top_recommendations"]]
    assert any(c in top_crops for c in ["wheat", "maize", "chickpea"])
