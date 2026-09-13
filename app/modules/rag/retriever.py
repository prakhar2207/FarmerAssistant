from typing import List, Dict, Any, Optional
from app.modules.rag.vector_store import vector_store

class AgriculturalRAG:
    """
    RAG interface connecting to the DenseVectorStore.
    Returns grounded ICAR/KVK documents and verifiable citations.
    """
    def __init__(self):
        self.store = vector_store

    def retrieve(self, query: str, top_k: int = 2, crop_hint: str = "") -> List[Dict[str, Any]]:
        """Backwards-compatible retrieve method returning top document chunks."""
        res = self.store.search(query=query, crop_hint=crop_hint, top_k=top_k)
        return res.get("chunks", [])

    def retrieve_with_citations(self, query: str, crop_hint: str = "", top_k: int = 2) -> Dict[str, Any]:
        """Returns structured RAG retrieval with citations and groundedness status."""
        return self.store.search(query=query, crop_hint=crop_hint, top_k=top_k)

agri_rag = AgriculturalRAG()
