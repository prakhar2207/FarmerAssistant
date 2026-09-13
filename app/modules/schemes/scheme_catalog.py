import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import DATA_DIR

SCHEMES_FILE = DATA_DIR / 'govt_schemes.json'

class SchemeCatalog:
    """Catalog of Indian Agricultural Welfare Schemes with verification provenance."""

    def __init__(self):
        self.schemes: List[Dict[str, Any]] = []
        self._load_schemes()

    def _load_schemes(self):
        if SCHEMES_FILE.exists():
            with open(SCHEMES_FILE, 'r', encoding='utf-8') as f:
                self.schemes = json.load(f)

    def search(self, query: str = '') -> List[Dict[str, Any]]:
        self._load_schemes()
        if not query:
            return self.schemes
        q = query.lower().strip()
        matched = []
        for s in self.schemes:
            if (q in s['name'].lower() or
                q in s['objective'].lower() or
                q in s.get('eligibility', '').lower() or
                q in s.get('benefits', '').lower() or
                q in s.get('ministry', '').lower()):
                matched.append(s)

        if matched:
            return matched

        # Token matching fallback
        tokens = [t for t in q.split() if len(t) > 2]
        for s in self.schemes:
            full_text = (s['name'] + ' ' + s['objective'] + ' ' + s.get('eligibility', '') + ' ' + s.get('benefits', '')).lower()
            if any(t in full_text for t in tokens):
                if s not in matched:
                    matched.append(s)

        return matched if matched else self.schemes

    def find_eligible_schemes(self, state: Optional[str] = None, land_acres: Optional[float] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        self._load_schemes()
        results = []
        for s in self.schemes:
            # Check landholding if specified in scheme
            max_land = s.get("max_land_holding_acres")
            if land_acres is not None and max_land is not None:
                if land_acres > max_land:
                    continue
            # Check state eligibility
            states = s.get("eligible_states", [])
            if state and states and "All India" not in states and state not in states:
                continue
            results.append(s)
        return results if results else self.schemes[:3]

scheme_catalog = SchemeCatalog()

def get_scheme_catalog() -> SchemeCatalog:
    return scheme_catalog

