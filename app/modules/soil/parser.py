import re
import io
import logging
from typing import Dict, Any, Optional, List
from pypdf import PdfReader

logger = logging.getLogger("krishi_saathi.soil_parser")

PLAUSIBILITY_LIMITS = {
    "ph": (3.5, 10.5),
    "ec": (0.01, 15.0),
    "oc": (0.05, 5.0),
    "n": (10.0, 1000.0),
    "p": (1.0, 250.0),
    "k": (10.0, 1200.0),
    "zn": (0.05, 50.0),
    "fe": (0.1, 100.0),
    "s": (0.5, 100.0),
    "b": (0.05, 20.0)
}

def parse_soil_text_or_pdf(
    file_bytes: Optional[bytes] = None,
    text_content: Optional[str] = None
) -> Dict[str, Any]:
    extracted_text = text_content or ''
    if file_bytes and not extracted_text:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted_text += (page.extract_text() or '') + "\n"
        except Exception as e:
            logger.warning(f"PDF extraction error: {e}")

    extracted_params: Dict[str, Dict[str, Any]] = {}
    missing_params: List[str] = []
    abnormal_warnings: List[str] = []

    patterns = {
        'ph': (r'\bph\b\s*[:=-]?\s*([0-9.]+)', ""),
        'ec': (r'\bec\b\s*[:=-]?\s*([0-9.]+)', "dS/m"),
        'oc': (r'\b(?:organic\s*carbon|जैविक\s*कार्बन|\boc\b)\s*[:=-]?\s*([0-9.]+)', "%"),
        'n': (r'\b(?:available\s*n|nitrogen|नाइट्रोजन|\bn\b)\s*[:=-]?\s*([0-9.]+)', "kg/ha"),
        'p': (r'\b(?:available\s*p|phosphorus|फास्फोरस|फॉस्फोरस|\bp\b)\s*[:=-]?\s*([0-9.]+)', "kg/ha"),
        'k': (r'\b(?:available\s*k|potassium|पोटाश|\bk\b)\s*[:=-]?\s*([0-9.]+)', "kg/ha"),
        'zn': (r'\b(?:zinc|जिंक|\bzn\b)\s*[:=-]?\s*([0-9.]+)', "ppm"),
        'fe': (r'\b(?:iron|लोहा|\bfe\b)\s*[:=-]?\s*([0-9.]+)', "ppm"),
        's': (r'\b(?:sulphur|sulfur|गंधक|सल्फर|\bs\b)\s*[:=-]?\s*([0-9.]+)', "ppm"),
        'b': (r'\b(?:boron|बोरॉन|\bb\b)\s*[:=-]?\s*([0-9.]+)', "ppm")
    }

    if extracted_text:
        for param, (regex, unit) in patterns.items():
            match = re.search(regex, extracted_text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    low, high = PLAUSIBILITY_LIMITS.get(param, (0.0, 9999.0))
                    is_abnormal = not (low <= val <= high)
                    if is_abnormal:
                        abnormal_warnings.append(f"{param.upper()} value {val} is outside normal agronomic range ({low}-{high} {unit}).")

                    extracted_params[param] = {
                        "value": val,
                        "unit": unit,
                        "is_extracted": True,
                        "is_abnormal": is_abnormal
                    }
                except ValueError:
                    missing_params.append(param)
            else:
                missing_params.append(param)
    else:
        missing_params = list(patterns.keys())

    total_keys = len(patterns)
    found_keys = len(extracted_params)
    confidence = round((found_keys / total_keys) * 100, 1)
    flat_values = {k: v["value"] for k, v in extracted_params.items()}

    return {
        "success": True,
        "is_report_parsed": found_keys > 0,
        "extraction_confidence": confidence,
        "extracted_parameters": flat_values,
        "detailed_parameters": extracted_params,
        "missing_parameters": missing_params,
        "abnormal_warnings": abnormal_warnings,
        "raw_snippet": (extracted_text.strip()[:300] + "...") if len(extracted_text.strip()) > 300 else extracted_text.strip()
    }

def extract_soil_metrics_from_text(text: str) -> Dict[str, Any]:
    res = parse_soil_text_or_pdf(text_content=text)
    params = res.get("extracted_parameters", {})
    return {
        "has_metrics": len(params) > 0,
        "ph": params.get("ph"),
        "nitrogen": params.get("n"),
        "phosphorus": params.get("p"),
        "potassium": params.get("k"),
        "organic_carbon": params.get("oc"),
        "details": res
    }

