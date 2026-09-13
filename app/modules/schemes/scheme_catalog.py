import json
from pathlib import Path
from typing import List, Dict, Any

SCHEMES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "govt_schemes.json"

class GovtSchemesCatalog:
    def __init__(self):
        self.schemes = []
        self._load_schemes()

    def _load_schemes(self):
        if SCHEMES_PATH.exists():
            with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
                self.schemes = json.load(f)

    def search(self, query: str = "") -> List[Dict[str, Any]]:
        if not self.schemes:
            self._load_schemes()
            
        if not query.strip():
            return self.schemes

        query_lower = query.lower()
        results = []
        for s in self.schemes:
            searchable = (
                s.get("name", "") + " " +
                s.get("objective", "") + " " +
                s.get("benefits", "")
            ).lower()
            if any(term in searchable for term in query_lower.split()):
                results.append(s)

        return results if results else self.schemes[:3]

scheme_catalog = GovtSchemesCatalog()
