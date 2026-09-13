import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("krishi_saathi.remedies")
KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "disease_knowledge.json"

def load_disease_knowledge() -> Dict[str, Any]:
    """Loads authoritative disease agronomic knowledge from decoupled JSON repository."""
    if KNOWLEDGE_PATH.exists():
        try:
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading disease_knowledge.json: {e}")
    return {}

DISEASE_CATALOG = load_disease_knowledge()
