import os
try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    from elevenlabs import ElevenLabs
from utils.env import clean_env

ELEVENLABS_API_KEY = clean_env("ELEVENLABS_API_KEY")
# Default to a female ("lady") voice — Rachel. Override via ELEVENLABS_VOICE_ID.
ELEVENLABS_VOICE_ID = clean_env("ELEVENLABS_VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"

# 1-second silent MP3 fallback when API key is absent
MOCK_MP3_SILENCE = (
    b'\xff\xf3\x44\xc0\x00\x00\x00\x03\x48\x00\x00\x00\x00\x4c\x41\x4d\x45\x33\x2e\x39\x38'
    b'\x2e\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
)


async def generate_voice(text: str, voice_type: str = "chat") -> bytes:
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY.startswith("your_"):
        print("[ELEVENLABS] No API key set — returning silent fallback.")
        return MOCK_MP3_SILENCE

    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio_generator = client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True,
            },
        )
        return b"".join(audio_generator)
    except Exception as e:
        print(f"[ELEVENLABS ERROR] TTS failed: {e} — returning silent fallback.")
        return MOCK_MP3_SILENCE
