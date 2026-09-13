from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    label: str
    confidence: float

class VisionContext(BaseModel):
    has_image: bool = False
    crop_detected: Optional[str] = None
    disease_key: Optional[str] = None
    disease_name_hi: Optional[str] = None
    disease_name_en: Optional[str] = None
    confidence_score: float = 0.0
    confidence_tier: str = "low"  # high, medium, low
    bounding_boxes: List[BoundingBox] = Field(default_factory=list)
    severity_percentage: float = 0.0
    needs_symptom_clarification: bool = False
    clarifying_questions: List[str] = Field(default_factory=list)
    escalation_required: bool = False
    escalation_note: Optional[str] = None

class WeatherContext(BaseModel):
    location: str = "Lucknow"
    temperature: float = 28.0
    humidity: int = 65
    wind_speed: float = 8.0
    rain_probability_48h: int = 0
    condition: str = "Clear"
    is_safe_for_spraying: bool = True
    spray_warning: Optional[str] = None

class SoilContext(BaseModel):
    ph: Optional[float] = None
    ec: Optional[float] = None
    oc: Optional[float] = None
    n: Optional[float] = None
    p: Optional[float] = None
    k: Optional[float] = None
    deficiencies: List[str] = Field(default_factory=list)

class RAGCitation(BaseModel):
    source: str
    authority: str  # ICAR, KVK, SAU, CIBRC
    title: str
    relevance_score: float
    snippet: str

class StatusBadge(BaseModel):
    step_key: str
    label_hi: str
    label_en: str
    status: str = "completed"  # pending, completed, warning

class AgriculturalContext(BaseModel):
    session_id: str = "default_session"
    farmer_id: str = "default_farmer"
    query_text: str = ""
    language: str = "hi"  # 'hi' or 'en'
    intent: str = "GENERAL_AGRI"
    slots: Dict[str, Any] = Field(default_factory=dict)
    
    farmer_profile: Dict[str, Any] = Field(default_factory=dict)
    weather: WeatherContext = Field(default_factory=WeatherContext)
    soil: SoilContext = Field(default_factory=SoilContext)
    vision: VisionContext = Field(default_factory=VisionContext)
    rag_citations: List[RAGCitation] = Field(default_factory=list)
    rag_grounded: bool = False
    
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    safety_passed: bool = True
    safety_violations: List[str] = Field(default_factory=list)
    status_badges: List[StatusBadge] = Field(default_factory=list)
    final_response: str = ""
    follow_up_suggestions: List[str] = Field(default_factory=list)
