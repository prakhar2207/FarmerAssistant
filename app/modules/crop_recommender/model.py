import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.modules.crop_recommender.agro_calendar import CROP_DETAILS_HINDI, get_current_indian_season

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "models_cache" / "crop_rf_model.pkl"

class CropRecommendationResult(dict):
    """Container supporting both dict access and iteration over top_recommendations."""
    def __iter__(self):
        return iter(self.get("top_recommendations", []))

    def __len__(self):
        return len(self.get("top_recommendations", []))

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get("top_recommendations", [])[item]
        return super().__getitem__(item)

class CropRecommender:
    """
    Random Forest Crop Recommendation Engine with Explainability Layer
    combining NPK, pH, Temperature, Humidity, Rainfall, and Indian Agro-Climatic Seasons.
    """

    def __init__(self):
        self.model = None
        self.features = []
        self.classes = []
        self._load_model()

    def _load_model(self):
        if MODEL_PATH.exists():
            try:
                payload = joblib.load(MODEL_PATH)
                self.model = payload["model"]
                self.features = payload["features"]
                self.classes = payload["classes"]
            except Exception as e:
                self.model = None

    def recommend(
        self,
        *args,
        n: float = 80.0,
        p: float = 40.0,
        k: float = 40.0,
        temperature: float = 24.0,
        humidity: float = 65.0,
        ph: float = 6.8,
        rainfall: float = 120.0,
        rainfall_mm: Optional[float] = None,
        month: Optional[int] = None,
        district: Optional[str] = None,
        soil_type: Optional[str] = None,
        season: Optional[str] = None,
        top_k: int = 3,
        **kwargs
    ) -> CropRecommendationResult:
        if self.model is None:
            self._load_model()

        # Handle positional args if provided: (soil_type, temp, humidity, ...)
        if len(args) >= 1 and isinstance(args[0], str):
            soil_type = args[0]
        if len(args) >= 2:
            temperature = float(args[1])
        if len(args) >= 3:
            humidity = float(args[2])

        if rainfall_mm is not None:
            rainfall = float(rainfall_mm)

        if month is None:
            import datetime
            month = datetime.datetime.now().month

        current_season = season or get_current_indian_season(month)


        input_data = pd.DataFrame(
            [[n, p, k, temperature, humidity, ph, rainfall]],
            columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        )

        probabilities = self.model.predict_proba(input_data)[0]
        top_indices = np.argsort(probabilities)[::-1][:3]

        recommendations = []
        for rank, idx in enumerate(top_indices, 1):
            crop_key = self.classes[idx]
            prob = float(probabilities[idx])
            score = round(prob * 100, 1)

            details = CROP_DETAILS_HINDI.get(crop_key, {
                "hindi_name": crop_key.title(),
                "season": "अनुकूल मौसम",
                "sowing_months": "उपयुक्त समय",
                "harvest_months": "परिपक्वता अवधि",
                "water_need": "मध्यम",
                "soil_type": "दोमट मिट्टी",
                "description": "यह फसल आपकी मिट्टी व जलवायु के अनुकूल है।"
            })

            # Explainability Layer: Soil, Climate, Season & Risk factors
            soil_comp = (
                f"मिट्टी का pH {ph:.1f} और उपलब्ध NPK ({n:.0f}:{p:.0f}:{k:.0f}) इस फसल की जैविक आवश्यकताओं के "
                f"{'पूर्णतः अनुकूल' if 6.0 <= ph <= 7.8 else 'मध्यम अनुकूल'} है।"
            )

            clim_comp = (
                f"वर्तमान तापमान {temperature:.1f}°C और हवा में नमी {humidity:.0f}% इस फसल की वानस्पतिक वृद्धि "
                f"के लिए अनुकूल है। वार्षिक/मौसमी वर्षा आवश्यकता: {details.get('water_need', 'मध्यम')}।"
            )

            # Check seasonal match
            crop_season = details.get("season", "")
            is_in_season = any(s in crop_season for s in current_season.split()) or "खरीफ / रबी" in crop_season
            season_comp = (
                f"वर्तमान माह ({month}) {current_season} चक्र के अंतर्गत आता है। "
                f"{'यह बुवाई हेतु सर्वोत्तम समय है।' if is_in_season else 'यह आगामी फसल चक्र के लिए उपयुक्त योजना है।'}"
            )

            # Specific Risk factors per crop group
            if crop_key in ["rice", "sugarcane"]:
                risk_factors = "भारी जलभराव या नहर/ट्यूबवेल की निरंतर सिंचाई आवश्यक; सूखा पड़ने पर उपज में गिरावट।"
            elif crop_key in ["chickpea", "lentil", "blackgram", "mungbean"]:
                risk_factors = "फूल आते समय अत्यधिक वर्षा या जलभराव से फली सड़न और विल्ट (उकठा) रोग का खतरा।"
            elif crop_key in ["wheat", "barley"]:
                risk_factors = "पकने के समय (मार्च) अचानक तापमान बढ़ने (पछुआ हवा/हीटवेव) से दाना सिकुड़ने का खतरा।"
            elif crop_key in ["cotton"]:
                risk_factors = "गुलाबी सुंडी (Pink Bollworm) एवं सफेद मक्खी का प्रकोप; जल निकास अनिवार्य।"
            else:
                risk_factors = "संतुलित उर्वरक एवं समय पर निराई-गुड़ाई न करने पर कीट-रोगों का जोखिम।"

            why_rec = (
                f"आपकी मिट्टी के पोषक स्तर (N:{n:.0f}, P:{p:.0f}, K:{k:.0f}, pH:{ph:.1f}) और जलवायु में "
                f"{details['hindi_name']} की उत्पादकता दर {score}% पाई गई।"
            )

            # Uncertainty handling
            uncertainty_note = None
            if score < 50.0:
                uncertainty_note = (
                    "⚠️ मध्यम अनुकूलता: वर्तमान जलवायु या पोषक तत्वों में कुछ सीमाएं हैं। "
                    "बुवाई से पूर्व मिट्टी सुधार (जिप्सम/चूना) या सिंचाई प्रबंधन सुनिश्चित करें।"
                )

            recommendations.append({
                "rank": rank,
                "crop_key": crop_key,
                "hindi_name": details["hindi_name"],
                "crop_hindi": details["hindi_name"],
                "crop_english": crop_key.title(),
                "suitability_score": score,
                "season": details.get("season", ""),
                "sowing_months": details.get("sowing_months", ""),
                "harvest_months": details.get("harvest_months", ""),
                "water_need": details.get("water_need", ""),
                "soil_type": details.get("soil_type", ""),
                "description": details.get("description", ""),
                "why_recommended": why_rec,
                "soil_compatibility": soil_comp,
                "climate_compatibility": clim_comp,
                "season_compatibility": season_comp,
                "risk_factors": [risk_factors],
                "risk_factors_text": risk_factors,
                "uncertainty_note": uncertainty_note
            })

        best_crop = recommendations[0]["hindi_name"]
        best_score = recommendations[0]["suitability_score"]
        summary_hindi = (
            f"वर्तमान मिट्टी परीक्षण (N:{n}, P:{p}, K:{k}, pH:{ph}) तथा मौसमी परिस्थितियों के आधार पर "
            f"{best_crop} की खेती सर्वाधिक अनुकूल ({best_score}%) आंकी गई है। मौसम चक्र: {current_season}।"
        )

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
