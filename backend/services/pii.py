"""
Lightweight, dependency-free PII detector.

Scans extracted document text for common personally-identifiable information so
the system can flag sensitive documents and, where appropriate, raise their
sensitivity level. Regex-based and conservative — it reports *types* and counts,
never the raw matched values, so detection results are themselves safe to store.
"""
import re

# Each entry: (label, compiled regex). Order matters — more specific first.
_PATTERNS = [
    ("email",        re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')),
    ("ssn",          re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
    ("pan",          re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')),          # India PAN
    ("aadhaar",      re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')),       # India Aadhaar
    ("credit_card",  re.compile(r'\b(?:\d[ -]?){13,16}\b')),
    ("ip_address",   re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')),
    ("phone",        re.compile(r'(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)\d{3}[\s-]?\d{4}(?!\d)')),
]

# Friendly labels for the UI.
LABELS = {
    "email": "Email address",
    "ssn": "US SSN",
    "pan": "PAN number",
    "aadhaar": "Aadhaar number",
    "credit_card": "Credit/debit card",
    "ip_address": "IP address",
    "phone": "Phone number",
}


def detect_pii(text: str) -> dict:
    """Return {detected, types, counts} for PII found in `text`.

    Never returns the matched values themselves — only which categories were
    seen and how many times.
    """
    if not text:
        return {"detected": False, "types": [], "counts": {}}

    counts = {}
    masked = text
    for label, pattern in _PATTERNS:
        matches = pattern.findall(masked)
        if matches:
            counts[label] = len(matches)
            # Blank out matches so a card number isn't also counted as a phone.
            masked = pattern.sub(" ", masked)

    types = [LABELS[k] for k in counts]
    return {"detected": bool(counts), "types": types, "counts": counts}


def elevate_sensitivity(current: str, pii: dict) -> str:
    """If PII was found, ensure sensitivity is at least 'confidential'."""
    if not pii.get("detected"):
        return current
    order = ["public", "internal", "confidential", "strictly_confidential"]
    cur = (current or "internal").lower().replace(" ", "_")
    try:
        idx = order.index(cur)
    except ValueError:
        idx = 1
    return order[max(idx, 2)]  # at least 'confidential'
