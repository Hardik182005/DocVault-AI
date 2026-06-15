import { useRef, useState, useCallback, useEffect } from "react";
import { api } from "@/lib/api";

// Shared ElevenLabs text-to-speech hook. `speak(text, id)` toggles: calling it
// again with the same id stops playback. A generation token guarantees only the
// latest call ever plays and that stop() truly cancels in-flight audio.
export function useSpeak() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const genRef = useRef(0);
  const speakingIdRef = useRef<string | null>(null);
  const [speakingId, setSpeakingId] = useState<string | null>(null);

  const setSpeaking = useCallback((id: string | null) => {
    speakingIdRef.current = id;
    setSpeakingId(id);
  }, []);

  const stop = useCallback(() => {
    genRef.current += 1;
    if (audioRef.current) {
      try { audioRef.current.pause(); } catch { /* noop */ }
      audioRef.current = null;
    }
    setSpeaking(null);
  }, [setSpeaking]);

  const speak = useCallback(async (text: string, id = "default") => {
    if (speakingIdRef.current === id) { stop(); return; }
    const clean = (text || "").trim();
    if (!clean) return;
    stop();
    const myGen = genRef.current;
    setSpeaking(id);
    try {
      const url = await api.speak(clean);
      if (myGen !== genRef.current) { try { URL.revokeObjectURL(url); } catch { /* noop */ } return; }
      const audio = new Audio(url);
      audioRef.current = audio;
      const cleanup = () => {
        try { URL.revokeObjectURL(url); } catch { /* noop */ }
        if (audioRef.current === audio) audioRef.current = null;
        if (myGen === genRef.current) setSpeaking(null);
      };
      audio.onended = cleanup;
      audio.onerror = cleanup;
      await audio.play();
    } catch {
      if (myGen === genRef.current) setSpeaking(null);
    }
  }, [stop, setSpeaking]);

  useEffect(() => () => stop(), [stop]);

  return { speaking: speakingId !== null, speakingId, speak, stop };
}

// Build a natural spoken analysis from a document's classification metadata.
export function buildDocSpeech(doc: any): string {
  const c = doc?.classification || {};
  const name = (doc?.filename || "this document").replace(/\.[^.]+$/, "");
  const type = (c.document_type || "document").replace(/_/g, " ");
  const sens = (c.sensitivity_level || "").replace(/_/g, " ");
  const parts = [`${name} is a ${type}.`];
  if (c.summary) parts.push(c.summary);
  if (sens) parts.push(`Its sensitivity level is ${sens}.`);
  if (Array.isArray(c.key_entities) && c.key_entities.length) {
    parts.push(`Key entities include ${c.key_entities.slice(0, 5).join(", ")}.`);
  }
  return parts.join(" ");
}

// Build a spoken overview of the whole knowledge base.
export function buildLibrarySpeech(docs: any[]): string {
  if (!docs || docs.length === 0) {
    return "There are no documents in your knowledge base yet. Upload some files to get started.";
  }
  const byType: Record<string, number> = {};
  docs.forEach(d => {
    const t = (d.classification?.document_type || "other").replace(/_/g, " ");
    byType[t] = (byType[t] || 0) + 1;
  });
  const groups = Object.entries(byType)
    .map(([t, n]) => `${n} ${t}${n > 1 ? "s" : ""}`)
    .join(", ");
  return `You have ${docs.length} document${docs.length > 1 ? "s" : ""} indexed: ${groups}.`;
}
