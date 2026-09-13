import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from app.modules.crop_recommender.agro_calendar import CROP_DETAILS_HINDI, get_current_indian_season

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models_cache" / "crop_rf_model.pkl"

class CropRecommender:
    def __init__(self):
        self.model = None
        self.features = []
        self.classes = []
        self._load_model()

    def _load_model(self):
        if MODEL_PATH.exists():
            payload = joblib.load(MODEL_PATH)
            self.model = payload["model"]
            self.features = payload["features"]
            self.classes = payload["classes"]

    def recommend(
        self,
        n: float = 80.0,
        p: float = 40.0,
        k: float = 40.0,
        temperature: float = 24.0,
        humidity: float = 65.0,
        ph: float = 6.8,
        rainfall: float = 120.0,
        month: int = 7
    ) -> Dict[str, Any]:
        if self.model is None:
            self._load_model()
            
        current_season = get_current_indian_season(month)
        import pandas as pd
        input_data = pd.DataFrame([[n, p, k, temperature, humidity, ph, rainfall]], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
        probabilities = self.model.predict_proba(input_data)[0]
        
        top_indices = np.argsort(probabilities)[::-1][:3]
        
        recommendations = []
        for idx in top_indices:
            crop_key = self.classes[idx]
            prob = float(probabilities[idx])
            details = CROP_DETAILS_HINDI.get(crop_key, {
                "hindi_name": crop_key.title(),
                "season": "अनुकूल मौसम",
                "sowing_months": "उपयुक्त समय",
                "harvest_months": "परिपक्वता अवधि",
                "water_need": "मध्यम",
                "description": "यह फसल आपकी मिट्टी व जलवायु के अनुकूल है।"
            })
            
            recommendations.append({
                "crop_key": crop_key,
                "hindi_name": details["hindi_name"],
                "suitability_score": round(prob * 100, 1),
                "season": details.get("season", ""),
                "sowing_months": details.get("sowing_months", ""),
                "harvest_months": details.get("harvest_months", ""),
                "water_need": details.get("water_need", ""),
                "description": details.get("description", "")
            })

        best_crop = recommendations[0]["hindi_name"]
        score = recommendations[0]["suitability_score"]
        summary_hindi = f"वर्तमान मिट्टी परीक्षण (N:{n}, P:{p}, K:{k}, pH:{ph}) तथा मौसम परिस्थितियों के आधार पर {best_crop} की खेती सर्वाधिक उपयुक्त ({score}%) रहेगी। वर्तमान मौसम: {current_season}।"

        return {
            "success": True,
            "current_season": current_season,
            "input_parameters": {
                "N": n, "P": p, "K": k,
                "temperature": temperature,
                "humidity": humidity,
                "pH": ph,
                "rainfall": rainfall
            },
            "top_recommendations": recommendations,
            "summary_hindi": summary_hindi
        }

crop_recommender = CropRecommender()
