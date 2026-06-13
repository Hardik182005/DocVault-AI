"""
Agentic RAG using LangChain AgentExecutor + Groq.
Retrieves chunks from ChromaDB and synthesizes cited answers.
"""
import os
import re
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from services.embedder import get_collection, get_model

SYSTEM_PROMPT = """You are BFAI, a friendly document intelligence assistant built to help users query and understand their uploaded documents.

RULES — follow these strictly:

GREETINGS & META QUESTIONS (no tool call needed):
- If the user says hello, hi, greet, asks who you are, what you do, or how to use you — respond warmly and introduce yourself. Do NOT call retrieve_chunks for these.
- Example intro: "Hi! I'm BFAI, your document intelligence assistant. Upload any PDF, image, or text file and I'll parse, classify, and index it so you can ask questions and get cited answers directly from your documents. What would you like to know?"

DOCUMENT QUESTIONS (always use the tool):
1. For any factual question about document content, ALWAYS call retrieve_chunks first.
2. Every factual claim MUST cite its source in the format [filename, p.N].
3. If retrieve_chunks returns no relevant results, say: "I couldn't find that in the uploaded documents. Try uploading a relevant file first, or rephrase your question."
4. Do NOT hallucinate page numbers or document names.
5. Be concise — lead with the answer, then cite the source."""


@tool
def retrieve_chunks(query: str) -> str:
    """Retrieve the most relevant document chunks for the given query. Always call this first."""
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


def run_rag_agent(message: str, conversation_history: list) -> dict:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
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

    # Convert history format
    from langchain_core.messages import HumanMessage, AIMessage
    lc_history = []
    for msg in conversation_history:
        if msg.get("role") == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    result = executor.invoke({"input": message, "chat_history": lc_history})
    answer = result["output"]

    # Parse citations from the answer text: look for [filename, p.N] patterns
    citation_pattern = r'\[([^\]]+),\s*p\.(\d+)\]'
    matches = re.findall(citation_pattern, answer)

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
