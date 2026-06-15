"""
Security utilities: file validation, sanitization.
python-magic import is optional — if libmagic is not installed, MIME check is skipped.
"""
import os
import re

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "image/png",
    "image/jpeg",
}
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg"}
MAX_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50)) * 1024 * 1024

# Try to import python-magic; fall back gracefully if libmagic not available
try:
    import magic as _magic
    _MAGIC_AVAILABLE = True
except Exception:
    _MAGIC_AVAILABLE = False


def validate_upload_file(filename: str, file_bytes: bytes) -> tuple:
    """Returns (is_valid, error_message)."""
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {ext} is not allowed. Allowed: {sorted(ALLOWED_EXTENSIONS)}"

    # Check size
    if len(file_bytes) > MAX_SIZE_BYTES:
        return False, f"File too large. Max size: {os.getenv('MAX_UPLOAD_SIZE_MB', 50)}MB"

    # Check actual MIME type (not just extension) — only if libmagic is available
    if _MAGIC_AVAILABLE:
        try:
            mime = _magic.from_buffer(file_bytes[:2048], mime=True)
            if mime not in ALLOWED_MIME_TYPES:
                return False, f"File content type '{mime}' does not match allowed types"
        except Exception:
            pass  # If MIME detection fails, proceed without blocking

    return True, ""


def sanitize_filename(filename: str) -> str:
    """Remove path traversal, special chars. Return safe filename."""
    # Strip directory components
    filename = os.path.basename(filename)
    # Remove anything that's not alphanumeric, dot, dash, underscore, or space
    filename = re.sub(r"[^\w\s\-.]", "", filename)
    filename = filename.strip()
    return filename or "unnamed_file"


def sanitize_chat_query(query: str) -> str:
    """Limit length and strip obvious injection patterns."""
    query = query[:500]  # Max 500 chars
    # Strip common prompt injection patterns
    for pattern in ["ignore previous instructions", "system:", "###", "```"]:
        query = query.replace(pattern, "")
    return query.strip()
