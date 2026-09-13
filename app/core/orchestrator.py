from typing import Dict, Any, List, Optional, Generator
from app.core.agent_state import AgentState
from app.core.graph import agent_graph, AgriculturalAgentGraph

class AgriculturalAgentOrchestrator:
    """
    Production-grade Agentic Orchestrator fusing:
    - Explicit State Machine Graph (AgriculturalAgentGraph)
    - Multimodal Query Input (Text + Image)
    - YOLO Foliar Disease Vision Detection
    - Real-time Open-Meteo Weather & Agro-climatic rules
    - Machine Learning Crop & Balanced Fertilizer recommendation
    - Genuine Dense Vector RAG grounded in ICAR/KVK repositories
    - CIBRC Chemical Safety & Weather Spraying Guardrails
    - User-friendly Status Badges (replacing raw model traces)
    - Real-time Server-Sent Events (SSE) Streaming
    """

    def __init__(self, graph: Optional[AgriculturalAgentGraph] = None):
        self.graph = graph or agent_graph

    def process_query(
        self,
        query: str,
        image_bytes: Optional[bytes] = None,
        session_id: str = "default_session",
        farmer_id: str = "default_farmer",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes full agent pipeline synchronously.
        """
        state = AgentState(
            raw_query=query,
            image_bytes=image_bytes,
            session_id=session_id,
            farmer_id=farmer_id,
            latitude=latitude,
            longitude=longitude,
            requested_lang=lang
        )
        final_state = self.graph.execute(state)
        return final_state.to_dict()

    def process_query_stream(
        self,
        query: str,
        image_bytes: Optional[bytes] = None,
        session_id: str = "default_session",
        farmer_id: str = "default_farmer",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        lang: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Executes full agent pipeline yielding SSE streaming events (badges, thoughts, text chunks).
        """
        state = AgentState(
            raw_query=query,
            image_bytes=image_bytes,
            session_id=session_id,
            farmer_id=farmer_id,
            latitude=latitude,
            longitude=longitude,
            requested_lang=lang
        )
        for event in self.graph.execute_stream(state):
            yield event

agent_orchestrator = AgriculturalAgentOrchestrator()
