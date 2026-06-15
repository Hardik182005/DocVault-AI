import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

load_dotenv()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="BFAI Document Intelligence API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Security headers middleware ───────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# ── CORS — use allow_origin_regex=".*" so any origin (including Firebase
#    preview URLs) is accepted during demo/deployment without hardcoding.
#    In production you would restrict this to known origins.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from routers import upload, chat, documents, insights
from routers.voice import router as voice_router

app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(voice_router, prefix="/api")
app.include_router(insights.router, prefix="/api")


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    storage_dir = os.getenv("STORAGE_DIR", "./storage")
    os.makedirs(os.path.join(storage_dir, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "pages"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "metadata"), exist_ok=True)
    os.makedirs(os.path.join(storage_dir, "chroma_db"), exist_ok=True)

    # Auto-ingest sample docs if ChromaDB is empty. Run in a background thread so
    # parsing/OCR of the bundled samples never blocks container readiness (Cloud
    # Run startup probe) — documents appear within a minute of first boot.
    def _ingest():
        try:
            from services.embedder import auto_ingest_samples
            auto_ingest_samples()
        except Exception as e:
            print(f"[BFAI] auto_ingest_samples skipped: {e}")

    import threading
    threading.Thread(target=_ingest, daemon=True).start()


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    try:
        from services.embedder import get_document_count
        count = get_document_count()
    except Exception:
        count = 0
    return {"status": "ok", "documents_indexed": count}
