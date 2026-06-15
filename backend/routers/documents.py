import os
import re
import json
import glob
import shutil
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def _validate_doc_id(doc_id: str):
    if not _UUID_RE.match(doc_id):
        raise HTTPException(status_code=400, detail="Invalid document ID — must be a UUID")


@router.get("/documents")
def list_documents():
    meta_dir = os.path.join(STORAGE_DIR, "metadata")
    os.makedirs(meta_dir, exist_ok=True)
    docs = []
    for path in glob.glob(os.path.join(meta_dir, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
            doc.pop("pages", None)  # keep the list lightweight; full text is in /documents/{id}
            docs.append(doc)
        except Exception:
            pass
    return sorted(docs, key=lambda x: x.get("indexed_at", ""), reverse=True)


def _reconstruct_pages_from_chroma(doc_id: str) -> list:
    """Rebuild per-page extracted text from indexed chunks, for documents that
    were ingested before per-page text was persisted in metadata."""
    try:
        from services.embedder import get_collection
        collection = get_collection()
        results = collection.get(where={"doc_id": {"$eq": doc_id}}, include=["documents", "metadatas"])
    except Exception:
        return []
    pages = {}
    for text, meta in zip(results.get("documents", []) or [], results.get("metadatas", []) or []):
        pn = meta.get("page_number", 1)
        pages.setdefault(pn, []).append((meta.get("chunk_index", 0), text))
    out = []
    for pn in sorted(pages):
        chunks = [t for _, t in sorted(pages[pn], key=lambda x: x[0])]
        out.append({"page_number": pn, "text": "\n".join(chunks)[:6000], "table_count": 0, "tables": []})
    return out


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    _validate_doc_id(doc_id)
    path = os.path.join(STORAGE_DIR, "metadata", f"{doc_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Document not found")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    # Backfill extracted text for older documents that have no stored pages.
    if not doc.get("pages"):
        doc["pages"] = _reconstruct_pages_from_chroma(doc_id)
    return doc


@router.get("/documents/{doc_id}/page/{page_number}/image")
def get_page_image(doc_id: str, page_number: int):
    _validate_doc_id(doc_id)
    if page_number < 1 or page_number > 1000:
        raise HTTPException(status_code=400, detail="Invalid page number")

    image_path = os.path.join(STORAGE_DIR, "pages", doc_id, f"page_{page_number}.png")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Page image not found")

    return FileResponse(image_path, media_type="image/png")


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    _validate_doc_id(doc_id)

    # Delete metadata file
    meta_path = os.path.join(STORAGE_DIR, "metadata", f"{doc_id}.json")
    if os.path.exists(meta_path):
        os.remove(meta_path)

    # Delete page images directory
    pages_dir = os.path.join(STORAGE_DIR, "pages", doc_id)
    if os.path.exists(pages_dir):
        shutil.rmtree(pages_dir)

    # Delete uploaded file (any extension)
    uploads_dir = os.path.join(STORAGE_DIR, "uploads")
    for candidate in glob.glob(os.path.join(uploads_dir, f"{doc_id}.*")):
        try:
            os.remove(candidate)
        except Exception:
            pass

    # Remove from ChromaDB
    try:
        from services.embedder import get_collection
        collection = get_collection()
        results = collection.get(where={"doc_id": {"$eq": doc_id}})
        if results["ids"]:
            collection.delete(ids=results["ids"])
    except Exception:
        pass

    return {"deleted": doc_id}
