import React, { useState, useRef, useEffect } from "react";
import { api } from "../api/client";

// Browser SpeechRecognition — Chrome/Edge expose it prefixed.
const SpeechRecognition =
  typeof window !== "undefined"
    ? (window.SpeechRecognition || window.webkitSpeechRecognition)
    : null;

// Global floating DocVault AI chat + voice orb — rendered in Layout so it shows on every route.
// Voice NEVER auto-starts — only fires when the user taps the mic button.
export default function VoiceOrb() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [voiceOn, setVoiceOn] = useState(false);       // TTS speaker toggle
  const [speakingIdx, setSpeakingIdx] = useState(null); // message currently playing
  const [listening, setListening] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState(""); // shown while mic is on
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! I'm DocVault AI. Ask me anything about your uploaded documents — I'll answer with exact citations showing the source page." }
  ]);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const audioRef = useRef(null);
  const recognitionRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    const c = messagesContainerRef.current;
    if (open && c) c.scrollTop = c.scrollHeight;
  }, [messages, open]);

  // Stop audio + mic when panel closes or unmounts
  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setSpeakingIdx(null);
  };

  useEffect(() => {
    if (!open) { stopAudio(); stopListening(); }
    return () => { stopAudio(); stopListening(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // ── Text-to-speech (ElevenLabs via api.speak) ──────────────────────────────
  const speak = async (text, idx) => {
    if (speakingIdx === idx) { stopAudio(); return; }
    stopAudio();
    setSpeakingIdx(idx); // Set immediately so the button shows "loading" state
    try {
      const url = await api.speak(text);
      if (audioRef.current?.src && audioRef.current.src !== url) return; // cancelled
      const audio = new Audio();
      audio.src = url;
      audioRef.current = audio;
      const cleanup = () => {
        try { URL.revokeObjectURL(url); } catch { /* noop */ }
        if (audioRef.current === audio) audioRef.current = null;
        setSpeakingIdx(s => (s === idx ? null : s));
      };
      audio.onended = cleanup;
      audio.onerror = () => { console.warn("[DocVault AI TTS] Audio error"); cleanup(); };
      await audio.play();
    } catch (e) {
      console.warn("[BFAI TTS] speak() error:", e);
      setSpeakingIdx(s => (s === idx ? null : s));
    }
  };

  // ── Voice input — Web Speech API with live transcript ─────────────────────
  const stopListening = () => {
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch { /* noop */ }
      recognitionRef.current = null;
    }
    // Also stop media recorder fallback if active
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      try { mediaRecorderRef.current.stop(); } catch { /* noop */ }
    }
    setListening(false);
    setLiveTranscript("");
  };

  const startListening = () => {
    if (listening) { stopListening(); return; }

    if (SpeechRecognition) {
      // Primary: Web Speech API — shows live transcript
      const rec = new SpeechRecognition();
      rec.lang = "en-IN";
      rec.interimResults = true; // enable live transcript
      rec.maxAlternatives = 1;
      rec.continuous = false;

      rec.onresult = (e) => {
        let interim = "";
        let final = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          const t = e.results[i][0].transcript;
          if (e.results[i].isFinal) final += t;
          else interim += t;
        }
        setLiveTranscript(interim || final);
        if (final) {
          setInput(final);
          setLiveTranscript("");
          stopListening();
        }
      };
      rec.onerror = () => stopListening();
      rec.onend = () => {
        setListening(false);
        setLiveTranscript("");
        recognitionRef.current = null;
      };

      recognitionRef.current = rec;
      setListening(true);
      try { rec.start(); } catch { stopListening(); }

    } else {
      // Fallback: MediaRecorder -> POST to /api/voice/transcribe
      navigator.mediaDevices?.getUserMedia({ audio: true }).then(stream => {
        const recorder = new MediaRecorder(stream);
        chunksRef.current = [];
        recorder.ondataavailable = e => chunksRef.current.push(e.data);
        recorder.onstop = async () => {
          stream.getTracks().forEach(t => t.stop());
          const blob = new Blob(chunksRef.current, { type: "audio/webm" });
          try {
            const result = await api.transcribe(blob);
            if (result?.text) setInput(result.text);
          } catch { /* ignore */ }
          setListening(false);
        };
        mediaRecorderRef.current = recorder;
        recorder.start();
        setListening(true);
        // Auto-stop after 10s
        setTimeout(() => {
          if (mediaRecorderRef.current?.state === "recording") {
            mediaRecorderRef.current.stop();
          }
        }, 10000);
      }).catch(() => setListening(false));
    }
  };

  // ── Chat with the RAG backend ──────────────────────────────────────────────
  const sendMessage = async (text) => {
    const trimmed = (text || "").trim();
    if (!trimmed || loading) return;
    const userMsg = { role: "user", text: trimmed };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const history = messages.map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: m.text }));
      const data = await api.chat(trimmed, history);
      const answer = data?.answer || "I couldn't process that. Try again.";
      let answerIdx = -1;
      setMessages(prev => {
        answerIdx = prev.length;
        return [...prev, { role: "assistant", text: answer, citations: data?.citations || [] }];
      });
      // TTS only if voice toggle is on — audio only plays after explicit user action
      if (voiceOn && answerIdx >= 0) {
        setTimeout(() => speak(answer, answerIdx), 50);
      }
    } catch {
      setMessages(prev => [...prev, { role: "assistant", text: "DocVault AI is unavailable right now. Please check the server is running.", citations: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-[60] w-[340px] max-w-[calc(100vw-3rem)] h-[460px] max-h-[70vh] bg-white rounded-2xl shadow-2xl border border-[#e8e4f0] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 bg-[#6434ed] text-white shrink-0">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>description</span>
              <div>
                <p className="text-[13px] font-bold leading-tight">DocVault AI</p>
                <p className="text-[10px] text-white/70 leading-none">
                  {listening ? (liveTranscript ? `"${liveTranscript}"` : "Listening…") : "Document Intelligence"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {/* TTS speaker toggle */}
              <button
                onClick={() => { const next = !voiceOn; setVoiceOn(next); if (!next) stopAudio(); }}
                aria-label={voiceOn ? "Turn off voice replies" : "Turn on voice replies"}
                title={voiceOn ? "Voice replies: on" : "Voice replies: off"}
                className="hover:opacity-80 p-0.5"
              >
                <span className="material-symbols-outlined text-[20px]" style={voiceOn ? { fontVariationSettings: "'FILL' 1" } : undefined}>
                  {voiceOn ? "volume_up" : "volume_off"}
                </span>
              </button>
              <button onClick={() => setOpen(false)} aria-label="Close chat" className="hover:opacity-80 p-0.5">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#fcf9f8]">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`group max-w-[80%] px-3 py-2 rounded-xl text-[13px] leading-relaxed ${
                  msg.role === "user"
                    ? "bg-[#6434ed] text-white rounded-br-sm"
                    : "bg-white text-gray-800 rounded-bl-sm border border-[#e8e4f0]"
                }`}>
                  {msg.text}
                  {msg.role === "assistant" && idx !== 0 && (
                    <button
                      onClick={() => speak(msg.text, idx)}
                      aria-label={speakingIdx === idx ? "Stop" : "Play voice"}
                      title={speakingIdx === idx ? "Stop" : "Play voice"}
                      className="ml-1.5 align-middle text-[#6434ed] hover:opacity-70"
                    >
                      <span className="material-symbols-outlined text-[15px] align-middle">
                        {speakingIdx === idx ? "stop_circle" : "volume_up"}
                      </span>
                    </button>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white border border-[#e8e4f0] px-3 py-2 rounded-xl rounded-bl-sm">
                  <span className="text-[12px] text-gray-400 animate-pulse">Thinking…</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-3 border-t border-[#e8e4f0] bg-white shrink-0">
            {/* Live transcript preview */}
            {listening && liveTranscript && (
              <p className="text-[11px] text-[#6434ed] mb-1.5 px-1 italic">"{liveTranscript}"</p>
            )}
            <div className="flex gap-2 items-center">
              {/* Mic button — voice only starts on explicit tap */}
              <button
                onClick={startListening}
                aria-label={listening ? "Stop listening" : "Speak your question"}
                title={listening ? "Stop listening" : "Speak your question (Speak button — tap to start)"}
                className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
                  listening ? "bg-red-500 text-white animate-pulse" : "bg-gray-100 text-[#6434ed] hover:bg-gray-200"
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">{listening ? "mic" : "mic_none"}</span>
              </button>
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) sendMessage(input); }}
                placeholder="Ask about your documents..."
                className="flex-1 bg-gray-50 rounded-lg px-3 py-2 text-[13px] text-gray-800 placeholder-gray-400 border border-[#e8e4f0] focus:outline-none focus:border-[#6434ed]"
              />
              <button
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || loading}
                aria-label="Send message"
                className="w-9 h-9 rounded-lg bg-[#6434ed] text-white flex items-center justify-center disabled:opacity-40 hover:opacity-90 transition-opacity shrink-0"
              >
                <span className="material-symbols-outlined text-[18px]">send</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating orb button */}
      <button
        onClick={() => setOpen(v => !v)}
        aria-label={open ? "Close DocVault AI assistant" : "Open DocVault AI assistant"}
        className="fixed bottom-6 right-6 z-[60] w-14 h-14 rounded-full bg-[#6434ed] text-white flex items-center justify-center shadow-xl hover:scale-105 active:scale-95 transition-transform"
      >
        <span className="material-symbols-outlined text-[26px]" style={{ fontVariationSettings: "'FILL' 1" }}>
          {open ? "close" : "description"}
        </span>
        {!open && (
          <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-purple-300 border-2 border-white animate-pulse" />
        )}
      </button>
    </>
  );
}
