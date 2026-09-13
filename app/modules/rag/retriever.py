import os
from typing import Dict, Any, List, Optional
from app.modules.rag.vector_store import DenseVectorStore, vector_store

class AgriRAGRetriever:
    """
    Production Agricultural RAG Retriever enforcing:
    - Dense Semantic Vector Store with cosine similarity
    - Strict relevance threshold (>= 0.50) to prevent hallucinated citations
    - Verifiable citation objects with source, document, authority, and section
    - Explicit clinical notice when query has no matching authoritative ICAR record
    """

    def __init__(self, store: Optional[DenseVectorStore] = None):
        self.store = store or vector_store

    def retrieve_with_citations(
        self,
        query: str,
        crop_filter: Optional[str] = None,
        top_k: int = 3,
        threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Retrieves matching authoritative guidelines and generates verified citation metadata.
        """
        search_res = self.store.search(query, crop_hint=crop_filter or "", top_k=top_k, threshold=threshold)
        
        if not search_res.get("grounded"):
            return {
                "has_grounding": False,
                "grounded": False,
                "context_text": "",
                "citations": [],
                "chunks": [],
                "unverified_notice": "इस प्रश्न के लिए ICAR संस्तुतियों में कोई प्रत्यक्ष मेल नहीं मिला। सामान्य कृषि सिद्धांतों के आधार पर मार्गदर्शन दिया जा रहा है।"
            }

        contexts = []
        for chunk in search_res.get("chunks", []):
            contexts.append(f"【{chunk.get('title', '')}】 ({chunk.get('source', '')}):\n{chunk.get('content', '')}")

        return {
            "has_grounding": True,
            "grounded": True,
            "context_text": "\n\n".join(contexts),
            "citations": search_res.get("citations", []),
            "chunks": search_res.get("chunks", []),
            "unverified_notice": None
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.50,
        crop_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        search_res = self.store.search(query, crop_hint=crop_filter or "", top_k=top_k, threshold=threshold)
        return search_res.get("chunks", [])

agri_rag = AgriRAGRetriever()

def get_rag_retriever() -> AgriRAGRetriever:
    return agri_rag

