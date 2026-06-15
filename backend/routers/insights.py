"""
Insights router — the "AI Audio Briefing" + per-document analysis agent.

GET /api/briefing      — LLM-synthesized executive briefing across the whole vault
GET /api/analyze/{id}  — autonomous analysis of a single document

Both return short, speech-friendly text that the frontend narrates via ElevenLabs.
Security-aware: the briefing explicitly surfaces confidential documents so a
listener is told what is sensitive before acting on it.
"""
import os
import re
import json
import glob
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from services.llm import complete, LLMUnavailable

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")

_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def _load_all_metadata() -> list:
    meta_dir = os.path.join(STORAGE_DIR, "metadata")
    docs = []
    for path in glob.glob(os.path.join(meta_dir, "*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                docs.append(json.load(f))
        except Exception:
            pass
    return docs


def _stats(docs: list) -> dict:
    by_type, by_sens = {}, {}
    confidential = []
    for d in docs:
        c = d.get("classification") or {}
        t = (c.get("document_type") or "other").replace("_", " ")
        s = (c.get("sensitivity_level") or "unknown").replace("_", " ")
        by_type[t] = by_type.get(t, 0) + 1
        by_sens[s] = by_sens.get(s, 0) + 1
        if "confidential" in (c.get("sensitivity_level") or ""):
            confidential.append(d.get("filename"))
    return {
        "total": len(docs),
        "by_type": by_type,
        "by_sensitivity": by_sens,
        "confidential_files": confidential,
    }


def _template_briefing(docs: list, st: dict) -> str:
    """Deterministic fallback briefing when no LLM is available."""
    if st["total"] == 0:
        return "Your knowledge base is empty. Upload some documents to get started."
    types = ", ".join(f"{n} {t}{'s' if n > 1 else ''}" for t, n in st["by_type"].items())
    parts = [f"Here is your document briefing. You have {st['total']} documents indexed: {types}."]
    if st["confidential_files"]:
        n = len(st["confidential_files"])
        parts.append(
            f"Security note: {n} document{'s are' if n > 1 else ' is'} marked confidential, "
            f"including {', '.join(os.path.splitext(f)[0] for f in st['confidential_files'][:3])}. Handle with care."
        )
    return " ".join(parts)


@router.get("/briefing")
@limiter.limit("15/minute")
def briefing(request: Request):
    docs = _load_all_metadata()
    st = _stats(docs)
    if st["total"] == 0:
        return {"briefing": _template_briefing(docs, st), "stats": st}

    # Compact, token-bounded digest for the LLM to synthesize from.
    digest_lines = []
    for d in docs[:40]:
        c = d.get("classification") or {}
        digest_lines.append(
            f"- {d.get('filename')}: type={c.get('document_type')}, "
            f"sensitivity={c.get('sensitivity_level')}, summary={(c.get('summary') or '')[:160]}"
        )
    digest = "\n".join(digest_lines)

    system = (
        "You are DocVault AI's analyst. Produce a concise spoken executive briefing "
        "(about 90-130 words) of a document knowledge base. It will be read aloud, so "
        "write flowing prose with no bullet points, markdown, or headings. Start with "
        "the total count and the mix of document types. Then call out the single most "
        "important finding. Then a one-line SECURITY note naming any confidential "
        "documents and advising care. End with one suggested question the user could ask."
    )
    user = f"Document inventory ({st['total']} docs):\n{digest}\n\nWrite the spoken briefing now."

    try:
        text = complete(system, user, temperature=0.3, max_tokens=320)
        text = re.sub(r'[#*`_]', '', text).strip()
        return {"briefing": text or _template_briefing(docs, st), "stats": st}
    except LLMUnavailable:
        return {"briefing": _template_briefing(docs, st), "stats": st}
    except Exception as e:
        print(f"[BRIEFING ERROR] {e}")
        return {"briefing": _template_briefing(docs, st), "stats": st}


@router.get("/analyze/{doc_id}")
@limiter.limit("20/minute")
def analyze_document(request: Request, doc_id: str):
    if not _UUID_RE.match(doc_id):
        raise HTTPException(status_code=400, detail="Invalid document ID")
    path = os.path.join(STORAGE_DIR, "metadata", f"{doc_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Document not found")
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    c = doc.get("classification") or {}

    system = (
        "You are DocVault AI's analyst. In about 60-90 words of spoken prose (no "
        "markdown, no bullets), tell the user what this document is, its single most "
        "important takeaway, and whether it is sensitive. End by confirming analysis is complete."
    )
    user = (
        f"Filename: {doc.get('filename')}\nType: {c.get('document_type')}\n"
        f"Sensitivity: {c.get('sensitivity_level')}\nKey entities: {c.get('key_entities')}\n"
        f"Summary: {c.get('summary')}\n\nWrite the spoken analysis now."
    )
    try:
        text = complete(system, user, temperature=0.3, max_tokens=240)
        text = re.sub(r'[#*`_]', '', text).strip()
    except Exception as e:
        print(f"[ANALYZE ERROR] {e}")
        name = os.path.splitext(doc.get("filename") or "this document")[0]
        text = (
            f"{name} is a {(c.get('document_type') or 'document').replace('_', ' ')}. "
            f"{c.get('summary') or ''} Analysis complete."
        )
    return {"analysis": text, "doc_id": doc_id}
