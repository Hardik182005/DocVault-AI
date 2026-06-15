// web/lib/api.ts — DocVault AI API client (Next.js / TypeScript)

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

async function request(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

export const api = {
  getHealth: () => request("/api/health"),

  uploadDocuments: (formData: FormData) =>
    fetch(`${API_BASE}/api/upload`, { method: "POST", body: formData }).then(r => r.json()),

  getProcessingStatus: (docId: string) => request(`/api/processing-status/${docId}`),

  getDocuments: () => request("/api/documents"),

  getDocument: (docId: string) => request(`/api/documents/${docId}`),

  deleteDocument: (docId: string) => request(`/api/documents/${docId}`, { method: "DELETE" }),

  getPageImageUrl: (docId: string, pageNumber: number) =>
    `${API_BASE}/api/documents/${docId}/page/${pageNumber}/image`,

  // docId (optional) focuses retrieval on a single document.
  chat: (message: string, conversationHistory: any[], docId: string | null = null) =>
    request("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_history: conversationHistory, doc_id: docId }),
    }),

  // Text-to-speech — returns object URL for audio (ElevenLabs via backend)
  speak: (text: string): Promise<string> =>
    fetch(`${API_BASE}/api/voice/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    }).then(r => { if (!r.ok) throw new Error(); return r.blob(); })
      .then(blob => {
        const audioBlob = blob.type.startsWith("audio/") ? blob : new Blob([blob], { type: "audio/mpeg" });
        return URL.createObjectURL(audioBlob);
      }),

  // Voice transcription fallback — field name MUST be "file" to match backend.
  transcribe: (blob: Blob) => {
    const formData = new FormData();
    formData.append("file", blob, "recording.webm");
    return fetch(`${API_BASE}/api/voice/transcribe`, { method: "POST", body: formData }).then(r => r.json());
  },

  // AI Audio Briefing — LLM executive briefing of the whole vault
  getBriefing: () => request("/api/briefing"),

  // Autonomous per-document analysis
  analyzeDocument: (docId: string) => request(`/api/analyze/${docId}`),

  health: () => request("/api/health").catch(() => null),
};
