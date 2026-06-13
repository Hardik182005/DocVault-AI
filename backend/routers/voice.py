"""
Voice router for BFAI Document Intelligence.
POST /voice/speak  — text-to-speech via ElevenLabs
POST /voice/transcribe — speech-to-text via OpenAI Whisper (server-side STT fallback)
"""
import io
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from services.elevenlabs_svc import generate_voice

router = APIRouter(prefix="/voice", tags=["voice"])
limiter = Limiter(key_func=get_remote_address)


class SpeakRequest(BaseModel):
    text: str


@router.post("/speak")
@limiter.limit("20/minute")
async def speak_text(request: Request, body: SpeakRequest):
    """Convert text to speech using ElevenLabs."""
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    text = text[:1000]  # Cap length to bound TTS latency / cost
    try:
        audio_bytes = await generate_voice(text, voice_type="chat")
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        print(f"[VOICE SPEAK ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe")
@limiter.limit("20/minute")
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """Transcribe an audio file using OpenAI Whisper (server-side STT fallback)."""
    import os
    from utils.env import clean_env
    try:
        from openai import OpenAI
        client = OpenAI(api_key=clean_env("OPENAI_API_KEY"))

        audio_bytes = await file.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = file.filename or "audio.webm"

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        return {"text": transcript.text}
    except Exception as e:
        print(f"[VOICE TRANSCRIBE ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
