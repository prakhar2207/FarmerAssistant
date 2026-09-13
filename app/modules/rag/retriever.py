import json
import re
from pathlib import Path
from typing import List, Dict, Any

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "icar_knowledge.json"

class AgriculturalRAG:
    def __init__(self):
        self.documents = []
        self._load_documents()

    def _load_documents(self):
        if KNOWLEDGE_PATH.exists():
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                self.documents = json.load(f)

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        if not self.documents:
            self._load_documents()
            
        tokens = re.findall(r"\w+", query.lower())
        if not tokens:
            return self.documents[:top_k]

        scored_docs = []
        for doc in self.documents:
            score = 0
            searchable_text = (
                doc.get("title", "") + " " +
                doc.get("crop", "") + " " +
                doc.get("content", "") + " " +
                " ".join(doc.get("tags", []))
            ).lower()

            for t in tokens:
                if len(t) < 2:
                    continue
                if t in doc.get("crop", "").lower():
                    score += 5
                elif t in " ".join(doc.get("tags", [])).lower():
                    score += 4
                elif t in doc.get("title", "").lower():
                    score += 3
                elif t in searchable_text:
                    score += 1

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored_docs[:top_k]]
        return results if results else self.documents[:top_k]

agri_rag = AgriculturalRAG()
