import os
import uuid
import time
from pathlib import Path
from typing import Tuple, Dict
from fastapi import HTTPException, UploadFile, status
from app.config import MAX_UPLOAD_SIZE_MB, UPLOADS_DIR, RATE_LIMIT_PER_MINUTE

# Magic byte signatures
MAGIC_NUMBERS = {
    b'\xff\xd8\xff': 'image/jpeg',
    b'\x89PNG\r\n\x1a\n': 'image/png',
    b'RIFF': 'image/webp',
    b'%PDF': 'application/pdf'
}

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}

# In-memory sliding window rate limiter
_rate_limits: Dict[str, list] = {}

def check_rate_limit(client_id: str, max_requests: int = RATE_LIMIT_PER_MINUTE, window_seconds: int = 60) -> bool:
    """Sliding-window rate limiter per client IP/session."""
    now = time.time()
    timestamps = _rate_limits.setdefault(client_id, [])
    # Remove timestamps older than window
    _rate_limits[client_id] = [t for t in timestamps if now - t < window_seconds]
    if len(_rate_limits[client_id]) >= max_requests:
        return False
    _rate_limits[client_id].append(now)
    return True

async def validate_and_save_upload(file: UploadFile, allowed_types: Tuple[str, ...] = ('image/', 'application/pdf')) -> Tuple[str, bytes]:
    """
    Validates uploaded file against size, extension, and magic bytes.
    Saves file with a random UUID name in isolated uploads directory.
    Returns (saved_filepath, file_bytes).
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="फ़ाइल उपलब्ध नहीं है। / No file uploaded."
        )

    # 1. Extension check
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"अमान्य फ़ाइल प्रकार ({ext})। केवल JPG, PNG, WEBP या PDF समर्थित हैं।"
        )

    # 2. Read bytes & check size limit
    contents = await file.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"फ़ाइल बहुत बड़ी है (अधिकतम {MAX_UPLOAD_SIZE_MB}MB अनुमत है)।"
        )

    # 3. Magic byte inspection
    is_valid_type = False
    for signature, mime in MAGIC_NUMBERS.items():
        if contents.startswith(signature):
            if any(mime.startswith(at) for at in allowed_types):
                is_valid_type = True
                break

    if not is_valid_type and not (ext == '.webp' and b'WEBP' in contents[:16]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="फ़ाइल का प्रारूप संदिग्ध या दूषित है। / File header does not match accepted format."
        )

    # 4. Save with isolated UUID filename
    safe_filename = f"{uuid.uuid4().hex}{ext}"
    target_path = UPLOADS_DIR / safe_filename
    with open(target_path, "wb") as f:
        f.write(contents)

    return str(target_path), contents
