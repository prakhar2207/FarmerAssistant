import re
import io
from typing import Dict, Any, Optional
from pypdf import PdfReader

def parse_soil_text_or_pdf(file_bytes: Optional[bytes] = None, text_content: Optional[str] = None) -> Dict[str, Any]:
    extracted_text = text_content or ''
    if file_bytes and not extracted_text:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                extracted_text += page.extract_text() or ''
        except Exception:
            pass
            
    # Default baseline values if not present
    parsed = {
        'ph': 7.1,
        'ec': 0.45,
        'oc': 0.52,
        'n': 235.0,
        'p': 12.5,
        'k': 175.0,
        'zn': 0.75,
        'fe': 5.1,
        's': 11.2
    }
    
    if extracted_text:
        # Regex search for common parameters
        ph_match = re.search(r'ph\s*[:=-]?\s*([0-9.]+)', extracted_text, re.IGNORECASE)
        if ph_match:
            try: parsed['ph'] = float(ph_match.group(1))
            except: pass
            
        ec_match = re.search(r'ec\s*[:=-]?\s*([0-9.]+)', extracted_text, re.IGNORECASE)
        if ec_match:
            try: parsed['ec'] = float(ec_match.group(1))
            except: pass
            
        oc_match = re.search(r'(?:oc|carbon|जैविक कार्बन)\s*[:=-]?\s*([0-9.]+)', extracted_text, re.IGNORECASE)
        if oc_match:
            try: parsed['oc'] = float(oc_match.group(1))
            except: pass
            
        n_match = re.search(r'(?:nitrogen|नाइट्रोजन|n)\s*[:=-]?\s*([0-9.]+)', extracted_text, re.IGNORECASE)
        if n_match:
            try: parsed['n'] = float(n_match.group(1))
            except: pass
            
        p_match = re.search(r'(?:phosphorus|फास्फोरस|p)\s*[:=-]?\s*([0-9.]+)', extracted_text, re.IGNORECASE)
        if p_match:
            try: parsed['p'] = float(p_match.group(1))
            except: pass
            
        k_match = re.search(r'(?:potassium|पोटाश|k)\s*[:=-]?\s*([0-9.]+)', extracted_text, re.IGNORECASE)
        if k_match:
            try: parsed['k'] = float(k_match.group(1))
            except: pass

    return parsed
