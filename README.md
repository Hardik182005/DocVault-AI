# DocVault AI — Document Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-38BDF8?logo=tailwindcss)](https://tailwindcss.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-orange)](https://groq.com/)
[![ElevenLabs](https://img.shields.io/badge/Voice-ElevenLabs-purple)](https://elevenlabs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deployed](https://img.shields.io/badge/Live-Firebase%20Hosting-red?logo=firebase)](https://docvault-ai-app.web.app)

> **Documents speak. DocVault translates.**

A Document Intelligence + Agentic RAG platform. Upload messy real-world documents (scanned PDFs, handwritten pages, image-heavy reports, tables) — the system extracts content with OCR, classifies each document with an LLM, and a chatbot answers questions with inline citations showing the exact source page as a thumbnail.

## Live Demo

| Service | URL |
|---------|-----|
| Frontend (Firebase) | https://docvault-ai-app.web.app |
| Backend API (Cloud Run) | https://bfai-hardik-backend-3692981377.asia-south1.run.app |
| API Health | https://bfai-hardik-backend-3692981377.asia-south1.run.app/api/health |
| API Docs | https://bfai-hardik-backend-3692981377.asia-south1.run.app/docs |

## Features

- **Smart Parser** — PDF (native + scanned), PNG/JPG (OCR), plain text. Tables extracted as structured data via pdfplumber. pytesseract fallback for scanned pages.
- **LLM Classifier** — Every document classified across type, topic, sensitivity level, and content characteristics. Structured JSON output via a multi-provider chain (OpenAI → Groq → Gemini) so classification never stalls on a single provider's rate limit.
- **Agentic RAG** — LangChain AgentExecutor with a ChromaDB retrieval tool. Grounded answers only — never hallucinates. Returns "I could not find relevant information" when nothing matches.
- **Resilient Parsing** — Per-page best-effort extraction: a single bad page, failed OCR, or unavailable renderer degrades gracefully instead of failing the whole upload. Every page is always guaranteed a rendered image so citations resolve.
- **Cited Answers** — Every answer includes `[filename, p.N]` citations. The cited page renders as a clickable thumbnail. Full-page modal on click.
- **Bulk Upload** — Drag-and-drop multi-file upload. Per-file status: Uploading → Parsing → Classifying → Indexing → ✓ Indexed. Real-time progress bar.
- **Voice Input** — Web Speech API live transcript as you speak. ElevenLabs TTS for voice replies. OpenAI Whisper server-side STT fallback. Voice NEVER auto-starts — only on explicit user action.
- **AI Audio Briefing** — One click generates an LLM-synthesized spoken executive briefing across the whole vault (document mix, key finding, a security note naming confidential docs) and narrates it via ElevenLabs.
- **Voice Analyst on Upload** — When a document finishes parsing, an autonomous analyst agent summarizes it and ElevenLabs announces the completed analysis.
- **Per-document Narration** — Every document card has a speak button that reads out its AI-extracted analysis; the library can announce which documents it holds.
- **Floating Voice Orb** — Global chat + voice assistant on every page.
- **Security** — File validation (extension + size + MIME), path traversal prevention, UUID-only doc IDs, slowapi rate limiting, security headers middleware.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Next.js 14 (App Router, TypeScript) + Tailwind          │
│  Landing → Chat (citations) → Upload → Documents         │
│  VoiceOrb (ElevenLabs TTS + Web Speech STT)              │
│  Full-site translate · PII redaction · AI Audio Briefing │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST (NEXT_PUBLIC_API_URL)
┌───────────────────────▼─────────────────────────────────┐
│  FastAPI Backend (Cloud Run)                             │
│  POST /api/upload     →  parser + classifier + PII + embed│
│  POST /api/chat       →  agentic RAG (doc-focus capable)  │
│  GET  /api/documents  →  metadata + per-page text         │
│  GET  /api/briefing   →  cross-document audio briefing    │
│  POST /api/voice/speak →  ElevenLabs TTS (female voice)   │
└───────┬──────────────┬──────────────┬───────────────────┘
        │              │              │
   pdfplumber     ChromaDB       OpenAI → Groq → Gemini
   pytesseract    (vectors)     (classify + RAG, auto-fallback)
   pdf2image      all-MiniLM
```

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS (Material Design 3 tokens) |
| Backend | FastAPI, Python 3.11, uvicorn |
| OCR/Parsing | pdfplumber, pdf2image, pytesseract |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB (persistent) |
| LLM | OpenAI gpt-4o-mini → Groq llama-3.3-70b → Gemini 2.5 Flash (auto-fallback) |
| Voice TTS | ElevenLabs v2 |
| Voice STT | Web Speech API (browser) + OpenAI Whisper (fallback) |
| Deployment | Google Cloud Run (backend), Firebase Hosting (frontend) |

## Security Decisions

### What we implemented
- **Upload layer**: Extension whitelist (.pdf, .png, .jpg, .txt), file size cap (50MB), MIME type check via python-magic, filename sanitization (no path traversal)
- **Storage layer**: Files stored with UUID names, not original filenames, preventing path-based attacks
- **Processing layer**: Document IDs validated as UUIDs before any filesystem access; regex guard on all doc_id parameters. **PII detection** scans extracted text for emails, phone numbers, cards, SSN, Aadhaar, PAN and IPs — flagged documents are auto-elevated to at least *confidential* sensitivity. Detection stores only the PII *categories* and counts, never the raw values.
- **API / retrieval layer**: Rate limiting (10/min upload, 30/min chat) via slowapi; chat query sanitized to strip injection patterns; security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection) on all responses
- **Secrets**: All API keys in environment variables / GCP Secret Manager — never in code

### What we considered but skipped
- Auth / JWT — not required for the demo scope; would add next
- Per-user document isolation — all docs are shared in the demo ChromaDB collection
- Redis for processing status — using in-memory dict; Redis would survive restarts

### What we'd add given more time
- User authentication (Firebase Auth)
- Per-user ChromaDB namespacing
- Streaming SSE responses for chat
- Document access control (sensitivity-based)

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for local full run)
- tesseract-ocr + poppler-utils (or use Docker)

### Local with Docker
```bash
git clone https://github.com/Hardik182005/DocVault-AI.git
cd DocVault-AI

# Create backend/.env from the example
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start everything
docker compose up --build
```
Frontend: http://localhost:5173  
Backend: http://localhost:8080  
API Docs: http://localhost:8080/docs

### Without Docker (manual)
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8080

# Frontend — Next.js (separate terminal)
cd web
cp .env.example .env.local        # set NEXT_PUBLIC_API_URL to your backend
npm install
npm run dev                        # http://localhost:3000
```

> The frontend is **Next.js 14 (App Router) + TypeScript** in `web/`. It is built
> as a static export (`npm run build` → `web/out`) and deployed to Firebase Hosting.

### Generate sample documents
```bash
pip install fpdf2
python generate_samples.py
```
This creates 5 sample documents in `sample_documents/` which are auto-ingested on first backend start.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check + indexed document count |
| `/api/upload` | POST | Upload 1–10 files (multipart/form-data) |
| `/api/processing-status/{doc_id}` | GET | Poll processing status |
| `/api/documents` | GET | List all indexed documents |
| `/api/documents/{doc_id}` | GET | Get single document metadata |
| `/api/documents/{doc_id}/page/{n}/image` | GET | Get page image PNG |
| `/api/documents/{doc_id}` | DELETE | Delete document + vectors |
| `/api/chat` | POST | Agentic RAG chat |
| `/api/voice/speak` | POST | ElevenLabs TTS |
| `/api/voice/transcribe` | POST | Whisper STT |
| `/api/briefing` | GET | AI Audio Briefing — LLM executive summary of the whole vault |
| `/api/analyze/{doc_id}` | GET | Autonomous per-document spoken analysis |

## Repository Structure

```
DocVault-AI/
├── web/               # Next.js 14 (App Router) + TypeScript frontend
│   ├── app/
│   │   ├── page.tsx           # Landing
│   │   ├── (app)/layout.tsx   # Dashboard shell (sidebar + nav + VoiceOrb)
│   │   └── (app)/{chat,upload,documents,settings}/page.tsx
│   ├── components/    # SideNavBar, TopNavBar, VoiceOrb, CitationCard, TranslateWidget
│   └── lib/           # api, useSpeak, redact, pageContext
├── backend/           # FastAPI
│   ├── routers/       # upload, chat, documents, voice, insights
│   ├── services/      # parser, classifier, embedder, rag_agent, security, pii, llm, elevenlabs_svc
│   ├── sample_documents/  # bundled into the image → auto-ingested on first run
│   └── Dockerfile
├── sample_documents/  # source sample docs (5+)
├── cloudbuild.yaml    # Cloud Run deploy
└── firebase.json      # Firebase Hosting (web/out)
```

## License
MIT
