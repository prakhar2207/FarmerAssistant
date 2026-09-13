from typing import Dict, Any
from app.modules.disease.yolo_service import yolo_leaf_service

class LeafDiseaseDetector:
    """
    Unified Leaf Disease Detector delegating to YoloLeafService.
    Preserves backwards compatibility for existing endpoints and tests.
    """
    def __init__(self):
        self.service = yolo_leaf_service

    def detect(self, image_bytes: bytes, crop_hint: str = "", rain_forecast: bool = False, lang: str = "hi") -> Dict[str, Any]:
        return self.service.infer(image_bytes=image_bytes, crop_hint=crop_hint, rain_forecast=rain_forecast, lang=lang)

disease_detector = LeafDiseaseDetector()
