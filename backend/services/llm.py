"""
Unified LLM access with multi-provider fallback.

Primary : Groq   (llama-3.3-70b-versatile)  — fast + free tier
Fallback: Gemini (gemini-1.5-flash)         — used if Groq fails / hits limit
Fallback: OpenAI (gpt-4o-mini, "ChatGPT")   — used if Gemini also fails

A provider is only attempted when its API key is configured. Gemini and OpenAI
are both called through the OpenAI SDK (Google exposes an OpenAI-compatible
endpoint), so no extra dependencies are required.
"""
from utils.env import clean_env

GROQ_MODEL   = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-1.5-flash"
OPENAI_MODEL = "gpt-4o-mini"

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Ordered fallback chain and the env var holding each provider's key.
ORDER = ["groq", "gemini", "openai"]
KEYS = {
    "groq":   "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
}


class LLMUnavailable(Exception):
    """Raised when every configured provider failed. Carries per-provider errors."""
    def __init__(self, errors):
        self.errors = errors  # list of (provider_name, error_message)
        super().__init__("; ".join(f"{n}: {m}" for n, m in errors) or "no providers configured")


def _key(name: str) -> str:
    v = clean_env(name)
    return "" if (not v or v.startswith("your_")) else v


def configured_providers() -> list:
    """Provider names (in fallback order) that have a usable API key."""
    return [p for p in ORDER if _key(KEYS[p])]


def is_rate_limit_error(err: str) -> bool:
    e = (err or "").lower()
    return any(s in e for s in (
        "429", "rate limit", "rate_limit", "ratelimit",
        "quota", "resource_exhausted", "insufficient_quota", "too many requests",
    ))


# ── Per-provider single-shot completion ─────────────────────────────────────
def _complete_groq(system, user, temperature, max_tokens):
    from groq import Groq
    client = Groq(api_key=_key("GROQ_API_KEY"))
    r = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=temperature, max_tokens=max_tokens,
    )
    return r.choices[0].message.content


def _complete_openai_compatible(api_key, base_url, model, system, user, temperature, max_tokens):
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=temperature, max_tokens=max_tokens,
    )
    return r.choices[0].message.content


def _complete_gemini(system, user, temperature, max_tokens):
    return _complete_openai_compatible(
        _key("GEMINI_API_KEY"), GEMINI_BASE_URL, GEMINI_MODEL,
        system, user, temperature, max_tokens)


def _complete_openai(system, user, temperature, max_tokens):
    return _complete_openai_compatible(
        _key("OPENAI_API_KEY"), None, OPENAI_MODEL,
        system, user, temperature, max_tokens)


_COMPLETERS = {
    "groq": _complete_groq,
    "gemini": _complete_gemini,
    "openai": _complete_openai,
}


def complete(system: str, user: str, temperature: float = 0.1,
             max_tokens: int = 900, skip: tuple = ()) -> str:
    """Single-shot completion that walks the fallback chain.

    Tries each configured provider in ORDER until one returns text. Providers in
    `skip` are not attempted (e.g. skip Groq when it already failed upstream).
    Raises LLMUnavailable with per-provider errors if all attempts fail.
    """
    errors = []
    for name in ORDER:
        if name in skip or not _key(KEYS[name]):
            continue
        try:
            txt = _COMPLETERS[name](system, user, temperature, max_tokens)
            if txt and txt.strip():
                return txt
            errors.append((name, "empty response"))
        except Exception as e:  # noqa: BLE001 — provider SDKs raise varied types
            errors.append((name, str(e)))
            print(f"[LLM] provider '{name}' failed: {e}")
    raise LLMUnavailable(errors)
