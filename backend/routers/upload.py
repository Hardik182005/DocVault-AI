import os
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address
from services.security import validate_upload_file, sanitize_filename
from services.parser import parse_document
from services.classifier import classify_document
from services.embedder import embed_document, _save_doc_metadata

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

# In-memory processing status store (use Redis in production)
processing_status: dict = {}


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_documents(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
):
    if len(files) > 10:
        return JSONResponse(status_code=400, content={"error": "Max 10 files per upload"})

    queued = []
    for file in files:
        file_bytes = await file.read()
        safe_name = sanitize_filename(file.filename or "unnamed")
        valid, error = validate_upload_file(safe_name, file_bytes)
        if not valid:
            queued.append({"filename": safe_name, "status": "rejected", "error": error})
            continue

        doc_id = str(uuid.uuid4())
        ext = os.path.splitext(safe_name)[1]
        upload_path = os.path.join(STORAGE_DIR, "uploads", f"{doc_id}{ext}")
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        with open(upload_path, "wb") as f:
            f.write(file_bytes)

        processing_status[doc_id] = {"status": "parsing", "progress": 10}
        background_tasks.add_task(process_document, doc_id, upload_path, safe_name)
        queued.append({"doc_id": doc_id, "filename": safe_name, "status": "queued"})

    return queued


async def process_document(doc_id: str, file_path: str, filename: str):
    try:
        processing_status[doc_id] = {"status": "parsing", "progress": 20}
        pages = parse_document(file_path, doc_id)

        processing_status[doc_id] = {"status": "classifying", "progress": 50}
        full_text = " ".join(p["text"] for p in pages)
        classification = classify_document(full_text, doc_id)

        # Detect PII and raise sensitivity if any is present.
        from services.pii import detect_pii, elevate_sensitivity
        pii = detect_pii(full_text)
        classification["pii"] = pii
        if pii["detected"]:
            classification["sensitivity_level"] = elevate_sensitivity(
                classification.get("sensitivity_level"), pii)

        processing_status[doc_id] = {"status": "embedding", "progress": 75}
        embed_document(doc_id, filename, pages, classification)
        _save_doc_metadata(doc_id, filename, len(pages), classification, pages)

        processing_status[doc_id] = {"status": "indexed", "progress": 100}
    except Exception as e:
        processing_status[doc_id] = {"status": "error", "progress": 0, "error": str(e)}


@router.get("/processing-status/{doc_id}")
def get_status(doc_id: str):
    return processing_status.get(doc_id, {"status": "unknown", "progress": 0})
