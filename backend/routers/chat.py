import re
from fastapi import APIRouter, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from services.rag_agent import run_rag_agent
from services.security import sanitize_chat_query

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []
    doc_id: str | None = None  # when set, focus retrieval on this one document


@router.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, body: ChatRequest):
    clean_message = sanitize_chat_query(body.message)
    if not clean_message:
        return {
            "answer": "Please enter a valid question.",
            "citations": [],
            "conversation_history": body.conversation_history,
        }
    # Validate doc_id format if focus mode is requested.
    doc_id = body.doc_id
    if doc_id and not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', doc_id):
        doc_id = None
    try:
        result = run_rag_agent(clean_message, body.conversation_history, doc_id=doc_id)
        return result
    except Exception as e:
        err = str(e)
        if "429" in err or "rate_limit" in err.lower():
            msg = "DocVault AI is temporarily unavailable — AI token limit reached. Resets at midnight UTC."
        else:
            print(f"[CHAT ERROR] {e}")
            msg = "DocVault AI encountered an error. Please try again in a moment."
        return {
            "answer": msg,
            "citations": [],
            "conversation_history": body.conversation_history,
        }
