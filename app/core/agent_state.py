from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class AgentState:
    """
    Typed state representation for KrishiSaathi Agentic Orchestration Graph.
    Tracks context, user slots, multimodal vision, tool execution, RAG citations, and safety.
    """
    # 1. Session & Farmer Profile
    session_id: str = "default_session"
    farmer_id: str = "default_farmer"
    farmer_profile: Dict[str, Any] = field(default_factory=dict)
    chat_history: List[Dict[str, Any]] = field(default_factory=list)

    # 2. Input Query & Modalities
    raw_query: str = ""
    image_bytes: Optional[bytes] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    requested_lang: Optional[str] = None

    # 3. Intent & Slot Extraction
    detected_language: str = "hi"
    intent: str = "GENERAL_AGRI"
    intent_confidence: float = 1.0
    crop: Optional[str] = None
    growth_stage: Optional[str] = None
    target_day: str = "today"
    action_type: Optional[str] = None
    symptoms: List[str] = field(default_factory=list)
    missing_slots: List[str] = field(default_factory=list)
    needs_clarification: bool = False
    clarification_question: Optional[str] = None

    # 4. Location & Agro-Climatic Context
    district: str = "Lucknow"
    location_label: str = "Lucknow, Uttar Pradesh"
    weather: Dict[str, Any] = field(default_factory=dict)
    temp: float = 28.0
    humidity: int = 65
    wind_speed: float = 8.0
    rain_prob: int = 10
    rain_amount_mm: float = 0.0
    rain_expected_48h: bool = False
    soil_data: Optional[Dict[str, Any]] = None

    # 5. Multimodal Vision
    vision_result: Optional[Dict[str, Any]] = None
    is_vision_rejected: bool = False

    # 6. Chemical & Agronomic Safety
    safety_violation: bool = False
    safety_details: Optional[Dict[str, Any]] = None

    # 7. Specialized Tool Execution & RAG
    tool_name: Optional[str] = None
    tool_output: str = ""
    tools_used: List[str] = field(default_factory=list)
    weather_used: bool = False
    soil_used: bool = False
    rag_used: bool = False
    rag_context: Dict[str, Any] = field(default_factory=dict)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    follow_up_suggestions: List[str] = field(default_factory=list)
    response_plan: Optional[Dict[str, Any]] = None

    # 8. Output & User Experience Badges
    final_response: str = ""
    status_badges: List[Dict[str, str]] = field(default_factory=list)
    thought_steps: List[str] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = False

    def add_badge(self, step_key: str, label_hi: str, label_en: str):
        self.status_badges.append({"step_key": step_key, "label_hi": label_hi, "label_en": label_en})

    def add_thought(self, step_msg: str):
        self.thought_steps.append(step_msg)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "response": self.final_response,
            "intent": self.intent,
            "crop": self.crop,
            "language": self.detected_language,
            "status_badges": self.status_badges,
            "thought_steps": self.thought_steps,
            "citations": self.citations,
            "follow_up_suggestions": self.follow_up_suggestions,
            "weather_summary": f"{self.location_label}: {self.temp}°C",
            "tools_used": self.tools_used
        }
        if self.vision_result:
            d["vision"] = self.vision_result
        if self.response_plan:
            d["response_plan"] = self.response_plan
        return d
