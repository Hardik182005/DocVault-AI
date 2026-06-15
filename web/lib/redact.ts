// Client-side PII redaction — mirrors the backend detector's categories so a
// user can instantly mask sensitive values in the extracted text they view.

const RULES: [string, RegExp][] = [
  ["EMAIL", /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g],
  ["SSN", /\b\d{3}-\d{2}-\d{4}\b/g],
  ["PAN", /\b[A-Z]{5}\d{4}[A-Z]\b/g],
  ["AADHAAR", /\b\d{4}\s?\d{4}\s?\d{4}\b/g],
  ["CARD", /\b(?:\d[ -]?){13,16}\b/g],
  ["IP", /\b(?:\d{1,3}\.){3}\d{1,3}\b/g],
  ["PHONE", /(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)\d{3}[\s-]?\d{4}/g],
];

export function redactPII(text: string): string {
  if (!text) return text;
  let out = text;
  for (const [label, re] of RULES) {
    out = out.replace(re, `█ [REDACTED ${label}] █`);
  }
  return out;
}
