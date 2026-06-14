# DocVault AI — Document Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
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
| Backend API (Cloud Run) | https://bfai-hardik-backend-[hash]-el.a.run.app |
| API Health | `/api/health` |
| API Docs | `/docs` |

## Features

- **Smart Parser** — PDF (native + scanned), PNG/JPG (OCR), plain text. Tables extracted as structured data via pdfplumber. pytesseract fallback for scanned pages.
- **LLM Classifier** — Every document classified across type, topic, sensitivity level, and content characteristics. Structured JSON output via Groq Llama 3.3.
- **Agentic RAG** — LangChain AgentExecutor with a ChromaDB retrieval tool. Grounded answers only — never hallucinates. Returns "I could not find relevant information" when nothing matches.
- **Cited Answers** — Every answer includes `[filename, p.N]` citations. The cited page renders as a clickable thumbnail. Full-page modal on click.
- **Bulk Upload** — Drag-and-drop multi-file upload. Per-file status: Uploading → Parsing → Classifying → Indexing → ✓ Indexed. Real-time progress bar.
- **Voice Input** — Web Speech API live transcript as you speak. ElevenLabs TTS for voice replies. OpenAI Whisper server-side STT fallback. Voice NEVER auto-starts — only on explicit user action.
- **Floating Voice Orb** — Global chat + voice assistant on every page.
- **Security** — File validation (extension + size + MIME), path traversal prevention, UUID-only doc IDs, slowapi rate limiting, security headers middleware.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Browser (React 19 + Vite + Tailwind)                   │
│  Landing → Chat (citations) → Upload → Documents        │
│  VoiceOrb (ElevenLabs TTS + Web Speech STT)             │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST
┌───────────────────────▼─────────────────────────────────┐
│  FastAPI Backend (Cloud Run)                             │
│  POST /api/upload    →  parser + classifier + embedder   │
│  POST /api/chat      →  agentic RAG agent               │
│  GET  /api/documents →  metadata store                   │
│  POST /api/voice/speak     →  ElevenLabs TTS            │
│  POST /api/voice/transcribe →  OpenAI Whisper           │
└───────┬──────────────┬──────────────┬───────────────────┘
        │              │              │
   pdfplumber     ChromaDB       Groq LLM
   pytesseract    (vectors)    llama-3.3-70b
   pdf2image      all-MiniLM   (classify + RAG)
```

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS (Material Design 3 tokens) |
| Backend | FastAPI, Python 3.11, uvicorn |
| OCR/Parsing | pdfplumber, pdf2image, pytesseract |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB (persistent) |
| LLM | Groq — llama-3.3-70b-versatile |
| Voice TTS | ElevenLabs v2 |
| Voice STT | Web Speech API (browser) + OpenAI Whisper (fallback) |
| Deployment | Google Cloud Run (backend), Firebase Hosting (frontend) |

## Security Decisions

### What we implemented
- **Upload layer**: Extension whitelist (.pdf, .png, .jpg, .txt), file size cap (20MB), MIME type check via python-magic, filename sanitization (no path traversal)
- **Storage layer**: Files stored with UUID names, not original filenames, preventing path-based attacks
- **Processing layer**: Document IDs validated as UUIDs before any filesystem access; regex guard on all doc_id parameters
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

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

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

## Repository Structure

```
DocVault-AI/
├── frontend/          # React 19 + Vite + Tailwind (DocVault design system)
│   └── src/
│       ├── pages/     # Chat, Upload, Documents, Landing, Settings
│       └── components/# SideNavBar, TopNavBar, VoiceOrb, CitationCard
├── backend/           # FastAPI
│   ├── routers/       # upload, chat, documents, voice
│   ├── services/      # parser, classifier, embedder, rag_agent, security
│   └── Dockerfile
├── sample_documents/  # 5 pre-loaded sample docs
├── generate_samples.py
└── docker-compose.yml
```

## License
MIT
