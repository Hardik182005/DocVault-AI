"""
Chunking + embedding + ChromaDB storage.
Also handles auto-ingestion of sample documents on first startup.
"""
import os
import uuid
import json
import glob
import datetime
from pathlib import Path

STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
CHROMA_PATH = os.path.join(STORAGE_DIR, "chroma_db")
SAMPLE_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents")

_model = None
_chroma_client = None
_collection = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _chroma_client.get_or_create_collection(
            name="bfai_documents",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_document(doc_id: str, filename: str, pages: list, classification: dict):
    """Chunk all pages, embed, and store in ChromaDB."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    collection = get_collection()
    model = get_model()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    chunk_id = 0
    for page in pages:
        full_text = page["text"]
        # Also include table content as text
        for table in page.get("tables", []):
            for row in table:
                full_text += " | ".join([str(c) for c in row if c]) + "\n"

        if not full_text.strip():
            continue

        chunks = splitter.split_text(full_text)
        for chunk in chunks:
            embedding = model.encode(chunk).tolist()
            collection.add(
                ids=[f"{doc_id}_p{page['page_number']}_c{chunk_id}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "doc_id": doc_id,
                    "doc_name": filename,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_id,
                    "doc_type": classification.get("document_type", "other"),
                    "sensitivity_level": classification.get("sensitivity_level", "internal"),
                }],
            )
            chunk_id += 1


def get_document_count() -> int:
    try:
        return get_collection().count()
    except Exception:
        return 0


def auto_ingest_samples():
    """If ChromaDB is empty, ingest all files in sample_documents/."""
    from services.parser import parse_document
    from services.classifier import classify_document

    if get_document_count() > 0:
        return  # Already has data

    sample_dir = SAMPLE_DOCS_DIR
    # Also try relative path for Docker context
    if not os.path.isdir(sample_dir):
        sample_dir = "./sample_documents"
    if not os.path.isdir(sample_dir):
        print("[BFAI] No sample_documents directory found — skipping auto-ingest.")
        return

    sample_files = glob.glob(os.path.join(sample_dir, "*"))
    for file_path in sample_files:
        if not os.path.isfile(file_path):
            continue
        try:
            doc_id = str(uuid.uuid4())
            filename = os.path.basename(file_path)
            pages = parse_document(file_path, doc_id)
            full_text = " ".join(p["text"] for p in pages)
            classification = classify_document(full_text, doc_id)
            embed_document(doc_id, filename, pages, classification)
            _save_doc_metadata(doc_id, filename, len(pages), classification)
            print(f"[BFAI] Auto-ingested sample: {filename}")
        except Exception as e:
            print(f"[BFAI] Failed to ingest {file_path}: {e}")


def _save_doc_metadata(doc_id: str, filename: str, page_count: int, classification: dict):
    meta_dir = os.path.join(STORAGE_DIR, "metadata")
    os.makedirs(meta_dir, exist_ok=True)
    with open(os.path.join(meta_dir, f"{doc_id}.json"), "w") as f:
        json.dump(
            {
                "doc_id": doc_id,
                "filename": filename,
                "page_count": page_count,
                "classification": classification,
                "indexed_at": str(datetime.datetime.utcnow()),
            },
            f,
        )
