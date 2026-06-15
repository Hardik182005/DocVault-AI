import { useRef, useState, useCallback, useEffect } from "react";
import { api } from "../api/client";

// Shared ElevenLabs text-to-speech hook.
// Returns { speaking, speakingId, speak, stop } so any page can play voice
// without re-implementing audio lifecycle. `speak(text, id)` toggles: calling
// it again with the same id stops playback.
export function useSpeak() {
  const audioRef = useRef(null);
  const genRef = useRef(0);            // bumped on every stop/new speak — invalidates in-flight plays
  const speakingIdRef = useRef(null);  // synchronous mirror of speakingId for race-free toggling
  const [speakingId, setSpeakingId] = useState(null);

  const setSpeaking = useCallback((id) => { speakingIdRef.current = id; setSpeakingId(id); }, []);

  const stop = useCallback(() => {
    genRef.current += 1;  // any pending api.speak() result will see a stale gen and abort
    if (audioRef.current) {
      try { audioRef.current.pause(); } catch { /* noop */ }
      audioRef.current = null;
    }
    setSpeaking(null);
  }, [setSpeaking]);

  const speak = useCallback(async (text, id = "default") => {
    // Tapping the same item again stops it (even while it's still loading).
    if (speakingIdRef.current === id) { stop(); return; }
    const clean = (text || "").trim();
    if (!clean) return;
    stop();                      // cancels anything currently playing or loading
    const myGen = genRef.current; // capture; if it changes, this call has been superseded
    setSpeaking(id);
    try {
      const url = await api.speak(clean);
      // A newer speak()/stop() happened while we were fetching — discard this audio.
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

  // Stop audio if the component using the hook unmounts.
  useEffect(() => () => stop(), [stop]);

  return { speaking: speakingId !== null, speakingId, speak, stop };
}

// Build a natural spoken analysis from a document's classification metadata.
export function buildDocSpeech(doc) {
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
export function buildLibrarySpeech(docs) {
  if (!docs || docs.length === 0) {
    return "There are no documents in your knowledge base yet. Upload some files to get started.";
  }
  const byType = {};
  docs.forEach(d => {
    const t = (d.classification?.document_type || "other").replace(/_/g, " ");
    byType[t] = (byType[t] || 0) + 1;
  });
  const groups = Object.entries(byType)
    .map(([t, n]) => `${n} ${t}${n > 1 ? "s" : ""}`)
    .join(", ");
  return `You have ${docs.length} document${docs.length > 1 ? "s" : ""} indexed: ${groups}.`;
}
