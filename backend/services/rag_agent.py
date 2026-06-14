"""
Agentic RAG using LangChain AgentExecutor + Groq.
Retrieves chunks from ChromaDB and synthesizes cited answers.
"""
import os
import re
from langchain_groq import ChatGroq
from utils.env import clean_env
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from services.embedder import get_collection, get_model
from services.llm import (
    complete, configured_providers, is_rate_limit_error,
    LLMUnavailable, GROQ_MODEL,
)

SYSTEM_PROMPT = """You are DocVault AI, a friendly document intelligence assistant built to help users query and understand their uploaded documents.

RULES — follow these strictly:

GREETINGS & META QUESTIONS (no tool call needed):
- If the user says hello, hi, greet, asks who you are, what you do, or how to use you — respond warmly and introduce yourself. Do NOT call retrieve_chunks for these.
- Example intro: "Hi! I'm DocVault AI, your document intelligence assistant. Upload any PDF, image, or text file and I'll parse, classify, and index it so you can ask questions and get cited answers directly from your documents. What would you like to know?"

DOCUMENT QUESTIONS (always use the tool):
1. For any factual question about document content, ALWAYS call retrieve_chunks first.
2. Every factual claim MUST cite its source in the format [filename, p.N].
3. If retrieve_chunks returns no relevant results, say: "I couldn't find that in the uploaded documents. Try uploading a relevant file first, or rephrase your question."
4. Do NOT hallucinate page numbers or document names.
5. Be concise — lead with the answer, then cite the source."""


def _retrieve(query: str) -> str:
    """Embed the query and return the most relevant document chunks as text."""
    collection = get_collection()
    model = get_model()
    embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=5,
        include=["documents", "metadatas", "distances"],
    )
    if not results["documents"] or not results["documents"][0]:
        return "NO_RESULTS"

    formatted = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist > 1.5:  # Too dissimilar — skip
            continue
        formatted.append(
            f"[SOURCE: {meta['doc_name']}, Page {meta['page_number']}]\n{doc}"
        )

    return "\n\n---\n\n".join(formatted) if formatted else "NO_RESULTS"


@tool
def retrieve_chunks(query: str) -> str:
    """Retrieve the most relevant document chunks for the given query. Always call this first."""
    return _retrieve(query)


def _run_groq_agent(message: str, lc_history: list) -> str:
    """Primary path: Groq agentic tool-calling. Raises on failure."""
    llm = ChatGroq(
        model=GROQ_MODEL,
        api_key=clean_env("GROQ_API_KEY"),
        temperature=0,
    )
    tools = [retrieve_chunks]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=3)
    result = executor.invoke({"input": message, "chat_history": lc_history})
    return result["output"]


def _run_fallback_rag(message: str, conversation_history: list) -> str:
    """Fallback path (Gemini -> OpenAI): retrieve chunks, then answer in one shot.

    Used when Groq is unavailable. Does manual RAG instead of tool-calling so it
    works through the OpenAI-compatible providers. Raises LLMUnavailable if every
    fallback provider fails too.
    """
    context = _retrieve(message)
    recent = conversation_history[-6:]
    history_txt = "\n".join(
        f"{m.get('role', 'user')}: {m.get('content', '')}" for m in recent
    ) or "(none)"

    user_prompt = (
        f"Conversation so far:\n{history_txt}\n\n"
        f"Retrieved document chunks:\n{context}\n\n"
        f"User question: {message}\n\n"
        "Answer the question using ONLY the retrieved chunks. Cite every factual "
        "claim as [filename, p.N] using the SOURCE labels above. If the chunks are "
        "'NO_RESULTS' and the user is greeting or asking who you are, introduce "
        "yourself warmly. If they ask something factual and nothing relevant was "
        "retrieved, say you couldn't find it in the uploaded documents."
    )
    # Skip Groq here — it already failed on the primary path.
    return complete(SYSTEM_PROMPT, user_prompt, temperature=0, max_tokens=900, skip=("groq",))


def run_rag_agent(message: str, conversation_history: list) -> dict:
    # Convert history format for the LangChain agent
    from langchain_core.messages import HumanMessage, AIMessage
    lc_history = []
    for msg in conversation_history:
        if msg.get("role") == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    answer = None
    errors = []  # (provider, message)

    # ── Primary: Groq agentic tool-calling ──────────────────────────────────
    if "groq" in configured_providers():
        try:
            answer = _run_groq_agent(message, lc_history)
        except Exception as e:
            errors.append(("groq", str(e)))
            print(f"[RAG] Groq agent failed, trying fallback: {e}")

    # ── Fallback: Gemini -> OpenAI manual RAG ───────────────────────────────
    if answer is None:
        try:
            answer = _run_fallback_rag(message, conversation_history)
        except LLMUnavailable as e:
            errors.extend(e.errors)
        except Exception as e:
            errors.append(("fallback", str(e)))
            print(f"[RAG] Fallback failed: {e}")

    # ── All providers exhausted ─────────────────────────────────────────────
    if answer is None:
        if errors and all(is_rate_limit_error(m) for _, m in errors):
            answer = (
                "DocVault AI is temporarily unavailable because all AI providers have hit "
                "their rate/token limits. Groq resets at midnight UTC. Please try again later."
            )
        else:
            print(f"[RAG AGENT ERROR] {errors}")
            answer = (
                "Sorry, I encountered an error while processing your request. "
                "Please try again in a moment."
            )
        return {
            "answer": answer,
            "citations": [],
            "conversation_history": conversation_history + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": answer},
            ],
        }

    # Parse citations from the answer text. Accept any of:
    #   [file, p.N]  [file, p N]  [file, pg.N]  [file, page N]  (case-insensitive)
    # Different providers format the page token differently (Groq -> "p.N",
    # Gemini/OpenAI often echo the "Page N" source label), so be liberal.
    citation_pattern = r'\[([^\],]+),\s*(?:p\.?|pg\.?|page)\s*(\d+)\]'
    matches = re.findall(citation_pattern, answer, re.IGNORECASE)

    citations = []
    collection = get_collection()
    seen = set()

    for doc_name, page_num in matches:
        key = (doc_name.strip(), page_num)
        if key in seen:
            continue
        seen.add(key)
        # Look up doc_id from metadata
        try:
            results = collection.get(
                where={
                    "$and": [
                        {"doc_name": {"$eq": doc_name.strip()}},
                        {"page_number": {"$eq": int(page_num)}},
                    ]
                },
                limit=1,
                include=["metadatas", "documents"],
            )
            if results["ids"]:
                meta = results["metadatas"][0]
                citations.append({
                    "doc_name": meta["doc_name"],
                    "doc_id": meta["doc_id"],
                    "page_number": int(page_num),
                    "chunk_text": results["documents"][0][:200] if results["documents"] else "",
                    "image_path": None,
                })
        except Exception:
            pass

    return {
        "answer": answer,
        "citations": citations,
        "conversation_history": conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ],
    }
