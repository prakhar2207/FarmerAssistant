try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sqlalchemy import text

from app.api.routes import router as api_router
from app.config import STATIC_DIR, ALLOWED_ORIGINS, APP_ENV, RATE_LIMIT_PER_MINUTE
from app.core.security import check_rate_limit
from app.db.session import engine
from app.modules.rag.retriever import agri_rag
from app.modules.disease.yolo_service import yolo_leaf_service
from app.modules.crop_recommender.model import crop_recommender

logger = logging.getLogger("krishi_saathi.gateway")

app = FastAPI(
    title="KrishiSaathi (कृषि साथी)",
    description="Hindi AI Agricultural Advisory & Agentic Farming Intelligence System",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only rate limit api endpoints excluding health
    if request.url.path.startswith("/api/") and not request.url.path.startswith("/api/health"):
        client_ip = request.client.host if request.client else "unknown"
        if not check_rate_limit(client_ip, max_requests=RATE_LIMIT_PER_MINUTE):
            return JSONResponse(
                status_code=429,
                content={"detail": "दर सीमा पार हो गई। कृपया थोड़ी देर बाद प्रयास करें। / Rate limit exceeded. Please wait a minute."}
            )
    return await call_next(request)

app.include_router(api_router, prefix="/api")

@app.get("/api/health")
def health_check():
    device = "cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"
    device_name = torch.cuda.get_device_name(0) if (TORCH_AVAILABLE and torch.cuda.is_available()) else "CPU"
    return {
        "status": "online",
        "health": "healthy",
        "system": "KrishiSaathi Agentic Advisory Engine",
        "environment": APP_ENV,
        "device": device,
        "device_name": device_name,
        "version": "2.0.0"
    }

@app.get("/api/readiness")
def readiness_check():
    """Checks all dependent services and models."""
    checks = {}
    is_ready = True

    # 1. Database
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok", "type": "sqlite_sqlalchemy"}
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}
        is_ready = False

    # 2. RAG Dense Vector Store
    try:
        doc_count = len(agri_rag.store.documents)
        checks["rag_knowledge"] = {"status": "ok" if doc_count > 0 else "degraded", "indexed_documents": doc_count}
    except Exception as e:
        checks["rag_knowledge"] = {"status": "error", "error": str(e)}

    # 3. Vision / YOLO Service
    checks["leaf_vision"] = {"status": "ok", "diseases_cataloged": len(yolo_leaf_service.catalog), "ready": True}

    # 4. Crop Recommender ML
    from app.modules.crop_recommender.agro_calendar import CROP_DETAILS_HINDI
    checks["crop_recommender"] = {"status": "ok", "crops_supported": len(crop_recommender.classes or CROP_DETAILS_HINDI)}


    status_code = 200 if is_ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks
        }
    )

# Mount static files for UI
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
