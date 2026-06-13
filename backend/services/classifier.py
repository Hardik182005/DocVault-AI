"""
LLM document classifier using Groq (free tier).
Input: extracted text from document
Output: structured JSON classification
"""
import os
import json
from groq import Groq
from utils.env import clean_env

client = Groq(api_key=clean_env("GROQ_API_KEY"))

CLASSIFICATION_PROMPT = """You are a document classifier. Analyze the provided document text and return ONLY a valid JSON object with NO preamble, NO markdown, NO backticks.

Required JSON schema:
{
  "document_type": "invoice|report|research_paper|legal|medical|financial|handwritten_note|presentation|email|other",
  "topic": "brief topic in 5 words max",
  "language": "en|hi|other",
  "content_characteristics": {
    "has_tables": boolean,
    "has_handwriting": boolean,
    "is_scanned": boolean,
    "has_images": boolean,
    "estimated_word_count": integer
  },
  "sensitivity_level": "public|internal|confidential|strictly_confidential",
  "sensitivity_reason": "one sentence explaining why",
  "key_entities": ["entity1", "entity2", "entity3"],
  "summary": "2 sentence summary of what this document is about",
  "tags": ["tag1", "tag2", "tag3"]
}

Return ONLY the JSON. Nothing else."""


def classify_document(text: str, doc_id: str) -> dict:
    # Use first 3000 chars to stay within context limits
    truncated = text[:3000]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": CLASSIFICATION_PROMPT},
                {"role": "user", "content": f"Document text:\n\n{truncated}"}
            ],
            temperature=0.1,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        # Strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        # Find the JSON object boundaries in case of any preamble
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        classification = json.loads(raw)
        classification["doc_id"] = doc_id
        return classification
    except Exception as e:
        # Return a safe fallback if LLM fails
        return {
            "doc_id": doc_id,
            "document_type": "other",
            "topic": "Unknown",
            "language": "en",
            "content_characteristics": {
                "has_tables": False,
                "has_handwriting": False,
                "is_scanned": False,
                "has_images": False,
                "estimated_word_count": 0,
            },
            "sensitivity_level": "internal",
            "sensitivity_reason": "Classification failed — defaulting to internal.",
            "key_entities": [],
            "summary": "Document could not be classified automatically.",
            "tags": [],
            "error": str(e),
        }
