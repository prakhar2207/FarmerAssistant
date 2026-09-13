import io
import pytest
from PIL import Image
import numpy as np
from app.modules.disease.detector import disease_detector

def test_disease_detection_synthetic_leaf():
    # Create a synthetic leaf image (mostly green with some yellow chlorosis)
    arr = np.zeros((128, 128, 3), dtype=np.uint8)
    arr[:, :, 1] = 180  # Green
    arr[40:80, 40:80, 0] = 170  # Yellow/chlorosis patch
    arr[40:80, 40:80, 1] = 170
    
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()
    
    res = disease_detector.detect(img_bytes, crop_hint="tomato", rain_forecast=True)
    assert res["success"] is True
    assert "disease_name_hindi" in res
    assert "confidence_score" in res
    assert res["confidence_score"] > 50
    assert "chemical_solution" in res
    # Rain forecast should trigger weather warning
    assert "मौसम चेतावनी" in res["weather_spray_advisory"]
