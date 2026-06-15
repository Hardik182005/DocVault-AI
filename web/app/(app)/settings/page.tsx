"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const DEFAULT_PREFS = {
  name: "",
  email: "",
  apiUrl: "http://localhost:8080",
  notifications: true,
  voiceEnabled: false,
};

function Section({ title, icon, children }: any) {
  return (
    <div className="glass-card rounded-xl card-inner-stroke overflow-hidden">
      <div className="px-6 py-4 border-b border-outline-variant/30 flex items-center gap-2">
        <span className="material-symbols-outlined text-primary text-lg">{icon}</span>
        <h3 className="font-title-md text-[15px] font-semibold text-on-surface">{title}</h3>
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
}

function Toggle({ label, description, value, onChange }: any) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-outline-variant/20 last:border-b-0">
      <div>
        <p className="text-sm font-medium text-on-surface">{label}</p>
        {description && <p className="text-xs text-on-surface-variant mt-0.5">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!value)}
        className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${value ? "bg-primary" : "bg-surface-container-high"}`}
      >
        <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform duration-200 ${value ? "translate-x-5" : "translate-x-0"}`} />
      </button>
    </div>
  );
}

export default function Settings() {
  const router = useRouter();
  const [prefs, setPrefs] = useState(DEFAULT_PREFS);
  const [saved, setSaved] = useState(false);
  const [apiStatus, setApiStatus] = useState<any>(null);
  const [apiLoading, setApiLoading] = useState(true);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem("bfai_prefs") || "{}");
      setPrefs(p => ({ ...p, ...stored }));
    } catch { /* ignore */ }

    api.health().then((d: any) => {
      setApiStatus(d);
      setApiLoading(false);
    }).catch(() => {
      setApiStatus(null);
      setApiLoading(false);
    });
  }, []);

  const set = (key: string, val: any) => setPrefs(p => ({ ...p, [key]: val }));

  const saveAll = () => {
    try {
      localStorage.setItem("bfai_prefs", JSON.stringify(prefs));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch { /* ignore */ }
  };

  const nameInitial = prefs.name ? prefs.name.charAt(0).toUpperCase() : "B";

  return (
    <div className="p-gutter max-w-container-max mx-auto w-full space-y-6">

      {/* ── Header ── */}
      <div className="glass-card rounded-xl p-6 card-inner-stroke flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-primary flex items-center justify-center text-white font-bold text-2xl shrink-0">
            {nameInitial}
          </div>
          <div>
            <h2 className="font-headline-lg text-title-lg font-bold text-on-surface tracking-tight">Settings</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {prefs.name || "Your Name"} · {prefs.email || "your@email.com"}
            </p>
          </div>
        </div>
        <button
          onClick={saveAll}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-label-caps text-sm font-bold transition-all ${
            saved
              ? "bg-tertiary text-white"
              : "bg-primary text-white hover:opacity-90"
          }`}
        >
          <span className="material-symbols-outlined text-sm">{saved ? "check_circle" : "save"}</span>
          {saved ? "Saved!" : "Save Changes"}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* ── Profile ── */}
        <Section title="Profile" icon="person">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-label-caps text-on-surface-variant mb-1.5">Display Name</label>
              <input
                value={prefs.name}
                onChange={e => set("name", e.target.value)}
                placeholder="Your Name"
                className="w-full bg-surface-container border border-outline-variant rounded-lg px-4 py-2.5 text-sm text-on-surface placeholder-on-surface-variant/50 focus:outline-none focus:border-primary transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-label-caps text-on-surface-variant mb-1.5">Email Address</label>
              <input
                value={prefs.email}
                onChange={e => set("email", e.target.value)}
                placeholder="your@email.com"
                type="email"
                className="w-full bg-surface-container border border-outline-variant rounded-lg px-4 py-2.5 text-sm text-on-surface placeholder-on-surface-variant/50 focus:outline-none focus:border-primary transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-label-caps text-on-surface-variant mb-1.5">Backend API URL</label>
              <input
                value={prefs.apiUrl}
                onChange={e => set("apiUrl", e.target.value)}
                placeholder="http://localhost:8080"
                className="w-full bg-surface-container border border-outline-variant rounded-lg px-4 py-2.5 text-sm font-data-mono text-on-surface focus:outline-none focus:border-primary transition-colors"
              />
              <p className="text-xs text-on-surface-variant mt-1">Override the backend URL (requires page reload)</p>
            </div>
          </div>
        </Section>

        {/* ── Voice & Notifications ── */}
        <Section title="Voice & Notifications" icon="notifications">
          <div>
            <Toggle
              label="Push Notifications"
              description="Get alerts for document processing completion"
              value={prefs.notifications}
              onChange={(v: boolean) => set("notifications", v)}
            />
            <Toggle
              label="AI Voice Replies"
              description="Enable ElevenLabs TTS — the assistant will speak answers after you send a message"
              value={prefs.voiceEnabled}
              onChange={(v: boolean) => set("voiceEnabled", v)}
            />
          </div>
        </Section>

      </div>

      {/* ── System Status ── */}
      <Section title="System Status" icon="monitor_heart">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

          {/* Backend */}
          <div className="bg-surface-container-lowest rounded-lg border border-outline-variant/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className={`w-2 h-2 rounded-full ${apiLoading ? "bg-yellow-500 animate-pulse" : apiStatus ? "bg-tertiary" : "bg-error"}`} />
              <span className="font-label-caps text-[10px] text-gray-500 font-bold tracking-widest">BACKEND</span>
            </div>
            <p className="font-data-mono text-sm text-on-surface font-bold">
              {apiLoading ? "Checking…" : apiStatus ? "Online" : "Offline"}
            </p>
            <p className="text-[10px] text-gray-500 mt-1">FastAPI · Python</p>
          </div>

          {/* Docs Indexed */}
          <div className="bg-surface-container-lowest rounded-lg border border-outline-variant/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-tertiary" />
              <span className="font-label-caps text-[10px] text-gray-500 font-bold tracking-widest">INDEXED</span>
            </div>
            <p className="font-data-mono text-sm text-on-surface font-bold">
              {apiStatus ? (apiStatus.documents_indexed ?? 0) : "—"}
            </p>
            <p className="text-[10px] text-gray-500 mt-1">Documents in ChromaDB</p>
          </div>

          {/* AI Stack */}
          <div className="bg-surface-container-lowest rounded-lg border border-outline-variant/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <span className="font-label-caps text-[10px] text-gray-500 font-bold tracking-widest">AI ENGINE</span>
            </div>
            <p className="font-data-mono text-sm text-on-surface font-bold">OpenAI · Groq</p>
            <p className="text-[10px] text-gray-500 mt-1">RAG + Classification</p>
          </div>

          {/* Voice TTS */}
          <div className="bg-surface-container-lowest rounded-lg border border-outline-variant/30 p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-primary" />
              <span className="font-label-caps text-[10px] text-gray-500 font-bold tracking-widest">VOICE TTS</span>
            </div>
            <p className="font-data-mono text-sm text-on-surface font-bold">ElevenLabs</p>
            <p className="text-[10px] text-gray-500 mt-1">eleven_multilingual_v2</p>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-outline-variant/30 flex items-center justify-between">
          <div className="text-xs text-gray-600 font-data-mono">
            DocVault AI v1.0 · Documents speak. DocVault AI translates.
          </div>
          <button
            onClick={() => router.push("/chat")}
            className="flex items-center gap-1 text-xs text-primary hover:underline font-label-caps font-semibold"
          >
            <span className="material-symbols-outlined text-sm">chat</span>
            Open Ask DocVault AI
          </button>
        </div>
      </Section>

    </div>
  );
}
