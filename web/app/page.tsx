"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

const HERO_DOCS = [
  { filename: "Q4_Annual_Report.pdf", type: "Financial Report", sensitivity: "confidential", verdict: "Revenue grew 18% YoY. Operating margin expanded to 24.3%. Board recommends final dividend of ₹12 per share.", pageCount: 48, icon: "description" },
  { filename: "Lab_Results_Scan.pdf", type: "Medical Record", sensitivity: "strictly_confidential", verdict: "Patient CBC within normal range. Lipid panel elevated — LDL 142 mg/dL. Follow-up in 3 months recommended.", pageCount: 3, icon: "biotech" },
  { filename: "Invoice_INV-2024-089.pdf", type: "Invoice", sensitivity: "internal", verdict: "Total amount due: ₹4,25,000. Line items include 3 service packages. Payment terms: Net-30.", pageCount: 2, icon: "receipt_long" },
  { filename: "Research_NLP_2024.pdf", type: "Research Paper", sensitivity: "public", verdict: "Novel attention mechanism improves BLEU score by 4.2 points on WMT benchmarks. 28-page technical study.", pageCount: 28, icon: "science" },
];

const SENSITIVITY_STYLES = {
  public:               { label: "Public",               cls: "bg-green-100 text-green-700" },
  internal:             { label: "Internal",             cls: "bg-blue-100 text-blue-700" },
  confidential:         { label: "Confidential",         cls: "bg-orange-100 text-orange-700" },
  strictly_confidential:{ label: "Strictly Confidential",cls: "bg-red-100 text-red-700" },
};

const PIPELINE_STEPS = [
  { icon: "upload_file",       label: "Upload",       desc: "Drop your file" },
  { icon: "document_scanner",  label: "Parse + OCR",  desc: "Text extracted from every page" },
  { icon: "label",             label: "Classify",     desc: "LLM classifies type + sensitivity" },
  { icon: "chat",              label: "Index + Chat", desc: "Ask anything with citations" },
];

export default function Landing() {
  const router = useRouter();

  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const currentDoc = HERO_DOCS[currentDocIndex];

  const [chartOffset, setChartOffset] = useState(1000);
  const [pipelineStep, setPipelineStep] = useState(0);
  const [isPipelineVisible, setIsPipelineVisible] = useState(false);
  const pipelineRef = useRef(null);
  const timers = useRef([]);

  useEffect(() => {
    const id = setInterval(() => setCurrentDocIndex(p => (p + 1) % HERO_DOCS.length), 5000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    setChartOffset(1000);
    const id = setTimeout(() => setChartOffset(0), 400);
    return () => clearTimeout(id);
  }, [currentDocIndex]);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !isPipelineVisible) {
        setIsPipelineVisible(true);
        runPipeline();
      }
    }, { threshold: 0.5 });
    if (pipelineRef.current) observer.observe(pipelineRef.current);
    return () => { if (pipelineRef.current) observer.unobserve(pipelineRef.current); };
  }, [isPipelineVisible]);

  useEffect(() => () => { timers.current.forEach(clearTimeout); }, []);

  const runPipeline = () => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setPipelineStep(0);
    [1, 2, 3, 4].forEach((step, i) => {
      const id = setTimeout(() => setPipelineStep(step), (i + 1) * 800);
      timers.current.push(id);
    });
  };

  const sens = SENSITIVITY_STYLES[currentDoc.sensitivity] || SENSITIVITY_STYLES.internal;

  return (
    <div className="bg-[#fcf9f8] text-[#1c1b1b] font-body-md text-body-md antialiased overflow-x-hidden select-none">

      {/* Marquee bar */}
      <div className="fixed top-0 left-0 w-full h-[40px] bg-purple-night z-50 overflow-hidden flex items-center shadow-md font-data-mono text-data-mono">
        <div className="absolute inset-0 w-1/4 bg-gradient-to-r from-white/10 to-transparent opacity-20 animate-scanline pointer-events-none" />
        <div className="flex whitespace-nowrap animate-marquee items-center text-[#e9e1ff] gap-16">
          {[0, 1].map(dup => (
            <div key={dup} className="flex items-center gap-8 px-4">
              {[
                { label: "DOCVAULT AI", val: "ONLINE", up: true },
                { label: "DOCS INDEXED", val: "5+", up: true },
                { label: "OCR ACCURACY", val: "99.2%", up: true },
                { label: "RAG LATENCY", val: "< 2s", up: true },
                { label: "GROQ LLAMA 3.3", val: "ACTIVE", up: true },
                { label: "ELEVENLABS TTS", val: "READY", up: true },
              ].map(({ label, val, up }) => (
                <span key={label} className="flex items-center gap-2">
                  <span className="text-white/70">{label}</span>
                  <span className="text-[#63fcc0]">{val}</span>
                  <span className="material-symbols-outlined text-[16px] text-[#63fcc0]" style={{ fontVariationSettings: "'FILL' 1" }}>
                    {up ? "arrow_upward" : "arrow_downward"}
                  </span>
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Navbar */}
      <nav className="fixed top-[40px] left-0 w-full z-40 bg-white/70 backdrop-blur-xl border-b border-[#cac3d9]/30 shadow-sm">
        <div className="flex justify-between items-center w-full px-8 h-[72px] max-w-[1440px] mx-auto">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#6434ed] flex items-center justify-center">
              <span className="material-symbols-outlined text-white text-[16px]" style={{ fontVariationSettings: "'FILL' 1" }}>description</span>
            </div>
            <span className="text-xl font-bold text-[#0d0d0d] tracking-tight font-title-md">DocVault AI</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <button onClick={() => window.scrollTo({top:0,behavior:"smooth"})} className="text-[#5317dd] font-bold border-b-2 border-[#5317dd] pb-1 font-label-caps text-[11px] tracking-widest">Home</button>
            <button onClick={() => document.getElementById("features")?.scrollIntoView({behavior:"smooth"})} className="text-[#484456] hover:text-[#5317dd] transition-colors font-label-caps text-[11px] tracking-widest">Features</button>
            <button onClick={() => document.getElementById("how-it-works")?.scrollIntoView({behavior:"smooth"})} className="text-[#484456] hover:text-[#5317dd] transition-colors font-label-caps text-[11px] tracking-widest">How it works</button>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => router.push("/chat")}
              className="hidden md:block font-label-caps text-xs tracking-wider text-[#484456] hover:text-[#5317dd] transition-colors font-semibold">
              Login
            </button>
            <button onClick={() => router.push("/upload")}
              className="bg-[#5317dd] text-white px-6 py-2.5 rounded font-label-caps text-xs tracking-wider hover:opacity-90 transition-all shadow-md font-bold">
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <header className="relative min-h-[920px] pt-[150px] pb-16 flex items-center justify-center overflow-hidden bg-white text-[#0d0d0d]">
        <div className="max-w-[1440px] mx-auto px-8 w-full grid md:grid-cols-2 gap-12 items-center relative z-10">
          <div className="space-y-8 text-left">
            <h1 className="font-display-hero text-display-hero tracking-tight text-charcoal flex flex-col gap-2 md:text-7xl md:leading-[1.1]">
              <div className="flex flex-wrap gap-x-4 gap-y-2">
                {"Documents speak.".split(" ").map((word, i) => (
                  <span key={i} className="overflow-hidden inline-flex pb-2">
                    <span className="inline-block animate-mask-up" style={{ animationDelay: `${i * 0.15}s`, transform: "translateY(120%) rotate(4deg)" }}>{word}</span>
                  </span>
                ))}
              </div>
              <div className="flex flex-wrap gap-x-4 gap-y-2">
                {"DocVault AI translates.".split(" ").map((word, i) => (
                  <span key={i} className="overflow-hidden inline-flex pb-2">
                    <span className="inline-block text-primary animate-mask-up" style={{ animationDelay: `${0.45 + i * 0.15}s`, transform: "translateY(120%) rotate(4deg)" }}>{word}</span>
                  </span>
                ))}
              </div>
            </h1>
            <p className="font-body-md text-lg text-[#484456] mt-6 leading-relaxed max-w-xl animate-fade-up" style={{ animationDelay: "0.8s", opacity: 0 }}>
              Upload scanned PDFs, handwritten notes, and messy reports.<br />
              Ask anything. Get grounded answers with exact source citations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 pt-4 animate-fade-up" style={{ animationDelay: "1s", opacity: 0 }}>
              <button onClick={() => router.push("/chat")}
                className="bg-[#5317dd] text-white px-8 py-3.5 rounded-lg font-label-caps text-sm tracking-wider hover:opacity-90 transition-all shadow-md font-bold uppercase flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">chat</span>
                Ask DocVault AI →
              </button>
              <button onClick={() => router.push("/upload")}
                className="border border-[#cac3d9] text-[#0d0d0d] px-8 py-3.5 rounded-lg font-label-caps text-sm tracking-wider hover:border-primary/50 hover:bg-surface-container-low transition-all font-bold uppercase flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">upload_file</span>
                ↑ Upload Documents
              </button>
            </div>
          </div>

          {/* Document card mockup */}
          <div className="relative hidden md:block w-full max-w-[500px] justify-self-center animate-fade-up" style={{ animationDelay: "0.4s", opacity: 0 }}>
            <div className="w-full rounded-2xl border border-[#cac3d9]/50 shadow-[0_20px_60px_rgba(0,0,0,0.06)] bg-white p-6 flex flex-col gap-4 transition-all duration-500">
              <div className="flex justify-between items-start border-b border-[#cac3d9]/30 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>{currentDoc.icon}</span>
                    <h3 className="font-data-mono text-[14px] text-[#0d0d0d] font-bold">{currentDoc.filename}</h3>
                  </div>
                  <p className="text-[12px] text-[#797487] mt-1">{currentDoc.type} · {currentDoc.pageCount} pages</p>
                </div>
                <span className={`inline-flex px-2 py-1 rounded-full text-[10px] font-bold ${sens.cls}`}>{sens.label}</span>
              </div>

              {/* Animated "extraction" bars */}
              <div className="flex-grow bg-[#fafafa] rounded border border-[#cac3d9]/20 p-3 space-y-2">
                {[85, 65, 90, 45, 72].map((w, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="h-1.5 bg-[#e9e1ff] rounded-full overflow-hidden" style={{ width: `${w}%` }}>
                      <div className="h-full bg-primary/60 rounded-full transition-all duration-1000" style={{
                        width: chartOffset === 0 ? "100%" : "0%",
                        transitionDelay: `${i * 0.15}s`
                      }} />
                    </div>
                    <span className="text-[9px] text-[#cac3d9] font-data-mono shrink-0">
                      {["EXTRACTED", "CLASSIFIED", "EMBEDDED", "INDEXED", "CITED"][i]}
                    </span>
                  </div>
                ))}
              </div>

              <div className="bg-[#5317dd]/5 rounded-lg p-4 border border-[#5317dd]/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className="material-symbols-outlined text-[#5317dd] text-[18px]">auto_awesome</span>
                  <span className="font-label-caps text-xs text-[#5317dd] font-bold">AI Summary</span>
                </div>
                <p className="font-body-md text-xs text-[#0d0d0d]/70 leading-relaxed">{currentDoc.verdict}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Trust bar */}
      <div className="bg-[#fafafa] border-b border-[#cac3d9] py-4 overflow-hidden">
        <div className="max-w-[1440px] mx-auto px-8 flex items-center gap-8 font-data-mono text-xs text-[#0d0d0d]/50 tracking-wider">
          <span className="uppercase font-bold shrink-0">Powered By</span>
          <div className="w-full overflow-hidden relative">
            <div className="absolute inset-y-0 left-0 w-12 bg-gradient-to-r from-[#fafafa] to-transparent z-10" />
            <div className="absolute inset-y-0 right-0 w-12 bg-gradient-to-l from-[#fafafa] to-transparent z-10" />
            <div className="flex whitespace-nowrap animate-marquee gap-16 items-center opacity-85">
              {[0, 1].map(dup => (
                <div key={dup} className="flex items-center gap-12">
                  {["PDFPLUMBER OCR", "CHROMADB VECTORS", "GROQ LLAMA 3.3", "SENTENCE TRANSFORMERS", "ELEVENLABS TTS", "OPENAI WHISPER STT", "FASTAPI BACKEND"].map((label, i) => (
                    <React.Fragment key={label}>
                      {i > 0 && <span className="w-1.5 h-1.5 rounded-full bg-[#cac3d9]/80" />}
                      <span>{label}</span>
                    </React.Fragment>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-white border-b border-[#cac3d9]/40 py-8">
        <div className="max-w-[1100px] mx-auto px-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            { value: "5+",    label: "Sample Docs Pre-Loaded" },
            { value: "4",     label: "AI Models in Stack" },
            { value: "< 2s",  label: "Avg RAG Latency" },
            { value: "100%",  label: "Grounded Answers" },
          ].map(({ value, label }) => (
            <div key={label}>
              <div className="text-[36px] font-bold text-[#5317dd] leading-none mb-1" style={{ fontFamily: "monospace" }}>{value}</div>
              <div className="text-[13px] text-[#797487]">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <section id="features" className="py-[90px] bg-[#fcf9f8] border-b border-[#cac3d9]/30">
        <div className="max-w-[1100px] mx-auto px-8">
          <div className="text-center mb-14">
            <span className="text-[11px] font-bold text-[#5317dd] tracking-[0.2em] uppercase block mb-3">What DocVault AI Does</span>
            <h2 className="text-[36px] md:text-[44px] font-bold text-[#0d0d0d] tracking-tight leading-tight">
              Every document. One intelligence layer.
            </h2>
            <p className="text-[16px] text-[#797487] mt-4 max-w-2xl mx-auto">
              Built for anyone who needs to extract meaning from messy, real-world documents fast.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: "document_scanner", color: "#5317dd", bg: "#f0ebff", title: "Smart Parser", desc: "Handles scanned PDFs, handwritten pages, embedded tables, image-heavy reports. Text + structure extracted per page." },
              { icon: "label",            color: "#0070f3", bg: "#e8f0ff", title: "LLM Classifier", desc: "Every doc classified across type, topic, sensitivity, and content characteristics. Output is structured JSON." },
              { icon: "hub",              color: "#007552", bg: "#e8fff7", title: "Agentic RAG", desc: "An AI agent retrieves the most relevant chunks and synthesizes answers. No hallucination. Grounded always." },
              { icon: "format_quote",     color: "#c67000", bg: "#fff3e0", title: "Cited Answers", desc: "Every answer shows the exact doc name + page number. The cited page renders as a thumbnail you can click." },
              { icon: "lock",             color: "#ba1a1a", bg: "#ffdad6", title: "Secure by Design", desc: "Upload validation, private storage, rate limiting, and sanitized retrieval at every layer." },
              { icon: "mic",             color: "#5317dd", bg: "#f0ebff", title: "Voice Input", desc: "Tap the mic and speak your question. Live transcript appears as you talk. Replies read aloud via ElevenLabs." },
            ].map(({ icon, color, bg, title, desc }) => (
              <div key={title} className="bg-white rounded-2xl p-6 border border-[#cac3d9]/40 hover:shadow-lg transition-shadow">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: bg }}>
                  <span className="material-symbols-outlined text-[22px]" style={{ color }}>{icon}</span>
                </div>
                <h3 className="font-semibold text-[16px] text-[#0d0d0d] mb-2">{title}</h3>
                <p className="text-[14px] text-[#797487] leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section id="how-it-works" ref={pipelineRef} className="py-[90px] bg-white border-b border-[#cac3d9]/30">
        <div className="max-w-[1100px] mx-auto px-8">
          <div className="text-center mb-14">
            <span className="text-[11px] font-bold text-[#5317dd] tracking-[0.2em] uppercase block mb-3">How It Works</span>
            <h2 className="text-[36px] font-bold text-[#0d0d0d]">Four steps. Total intelligence.</h2>
          </div>
          <div className="flex flex-col md:flex-row items-center justify-center gap-0">
            {PIPELINE_STEPS.map((step, i) => (
              <React.Fragment key={step.label}>
                <div className={`flex flex-col items-center text-center w-[200px] transition-all duration-500 ${pipelineStep > i ? "opacity-100 scale-100" : "opacity-30 scale-95"}`}>
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-3 transition-colors duration-500 ${pipelineStep > i ? "bg-[#5317dd] text-white shadow-lg shadow-[#5317dd]/30" : "bg-[#f0ebff] text-[#5317dd]"}`}>
                    <span className="material-symbols-outlined text-[28px]" style={{ fontVariationSettings: "'FILL' 1" }}>{step.icon}</span>
                  </div>
                  <p className="font-semibold text-[14px] text-[#0d0d0d]">{step.label}</p>
                  <p className="text-[12px] text-[#797487] mt-1">{step.desc}</p>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div className={`hidden md:block h-[2px] w-20 mx-2 rounded-full transition-colors duration-500 ${pipelineStep > i + 1 ? "bg-[#5317dd]" : "bg-[#e5e7eb]"}`} />
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="text-center mt-10">
            <button onClick={runPipeline} className="px-6 py-2.5 rounded-lg border border-[#5317dd]/30 text-[#5317dd] font-label-caps text-xs tracking-wider hover:bg-[#f0ebff] transition-colors">
              ↺ Replay Animation
            </button>
          </div>
        </div>
      </section>

      {/* How it works under the hood — detailed pipeline card */}
      <section className="py-[90px] bg-[#fcf9f8] border-b border-[#cac3d9]/30">
        <div className="max-w-[1100px] mx-auto px-8">
          <p className="text-center text-[11px] font-bold text-[#797487] tracking-[0.2em] uppercase mb-8">How it works under the hood</p>
          <div className="glass-card rounded-2xl card-inner-stroke p-8 md:p-10">
            <div className="flex flex-col md:flex-row items-stretch justify-between gap-4">
              {[
                { icon: "description", title: "Your Document", desc: "PDF, DOCX, TXT, scans", chips: [], card: null },
                { icon: "bolt", title: "DocVault Engine", desc: "OCR · Parse · Classify", chips: ["OCR", "Tables", "Classify", "Embed"], card: null, highlight: true },
                { icon: "data_object", title: "Structured Data", desc: "Text + Tables (JSON)", chips: [], card: ["12 pages", "3 tables", "JSON ✓"] },
                { icon: "auto_awesome", title: "OpenAI + RAG", desc: "Classify · Retrieve · Answer", chips: ["Grounded"], card: null },
                { icon: "verified", title: "Cited Answer", desc: "Grounded · No hallucination", chips: ["[doc, p.N]"], card: null },
              ].map((stage, i, arr) => (
                <React.Fragment key={stage.title}>
                  <div className="flex flex-col items-center text-center flex-1 min-w-[150px]">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-3 ${stage.highlight ? "bg-[#5317dd] text-white shadow-lg shadow-[#5317dd]/30" : "bg-[#f0ebff] text-[#5317dd]"}`}>
                      <span className="material-symbols-outlined text-[26px]" style={{ fontVariationSettings: "'FILL' 1" }}>{stage.icon}</span>
                    </div>
                    <p className="font-semibold text-[14px] text-[#0d0d0d]">{stage.title}</p>
                    <p className="text-[11px] text-[#797487] mt-1 mb-2">{stage.desc}</p>
                    {stage.card ? (
                      <div className="bg-[#5317dd]/5 border border-[#5317dd]/20 rounded-lg px-3 py-2 font-data-mono text-[10px] text-[#5317dd] space-y-0.5">
                        {stage.card.map(line => <div key={line}>{line}</div>)}
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-1 justify-center">
                        {stage.chips.map(c => (
                          <span key={c} className="text-[9px] font-semibold px-2 py-0.5 rounded-full bg-[#f0ebff] text-[#5317dd]">{c}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  {i < arr.length - 1 && (
                    <div className="hidden md:flex items-center justify-center shrink-0 pt-7">
                      <span className="text-[#cac3d9] text-xl">···</span>
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-between gap-2 mt-8 pt-6 border-t border-[#cac3d9]/30">
              <span className="flex items-center gap-2 text-[12px] text-[#797487]">
                <span className="w-2 h-2 rounded-full bg-[#005a3e] animate-pulse" />
                Pipeline active · Runs fully on free-tier infrastructure
              </span>
              <span className="flex items-center gap-1.5 text-[12px] font-semibold text-[#5317dd]">
                <span className="material-symbols-outlined text-[16px]">bolt</span>
                Powered by OpenAI · Groq Llama 3.3 · ChromaDB
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Pre-loaded Sample Library table */}
      <section className="py-[90px] bg-white border-b border-[#cac3d9]/30">
        <div className="max-w-[1100px] mx-auto px-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
            <div>
              <h2 className="text-[28px] md:text-[34px] font-bold text-[#0d0d0d] tracking-tight">Pre-loaded Sample Library</h2>
              <p className="text-[14px] text-[#797487] mt-1">5+ sample documents ship with DocVault AI so the chatbot works on first run.</p>
            </div>
            <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-full bg-purple-50 text-purple-700 self-start sm:self-auto">
              <span className="material-symbols-outlined text-[14px]">bolt</span>
              Auto-indexed on startup
            </span>
          </div>
          <div className="glass-card rounded-2xl card-inner-stroke overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-[13px]">
                <thead>
                  <tr className="border-b border-[#cac3d9]/40 bg-[#faf8ff]">
                    {["Document", "Type", "Topic", "Sensitivity", "Parsing"].map(h => (
                      <th key={h} className="px-5 py-3 font-label-caps text-[10px] tracking-widest text-[#797487] font-bold uppercase">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {[
                    { doc: "sample_invoice.pdf", type: "Invoice", topic: "Finance", sens: "internal", parse: "Tables · pdfplumber", icon: "table" },
                    { doc: "sample_report.pdf", type: "Report", topic: "Business", sens: "internal", parse: "Text · pdfplumber", icon: "description" },
                    { doc: "sample_research.pdf", type: "Research Paper", topic: "NLP / AI", sens: "public", parse: "Text + tables", icon: "science" },
                    { doc: "sample_medical.pdf", type: "Medical", topic: "Healthcare", sens: "strictly_confidential", parse: "OCR · Tesseract", icon: "biotech" },
                    { doc: "sample_notes.txt", type: "Meeting Notes", topic: "HR / Admin", sens: "internal", parse: "Plain text", icon: "text_snippet" },
                  ].map((r) => {
                    const sensMap: any = {
                      public: "bg-green-100 text-green-700",
                      internal: "bg-blue-100 text-blue-700",
                      confidential: "bg-orange-100 text-orange-700",
                      strictly_confidential: "bg-red-100 text-red-700",
                    };
                    return (
                      <tr key={r.doc} className="border-b border-[#cac3d9]/20 last:border-b-0 hover:bg-[#faf8ff] transition-colors">
                        <td className="px-5 py-3.5">
                          <span className="flex items-center gap-2 font-data-mono text-[12px] text-[#0d0d0d]">
                            <span className="material-symbols-outlined text-[#5317dd] text-[16px]">description</span>
                            {r.doc}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 text-[#484456]">{r.type}</td>
                        <td className="px-5 py-3.5 text-[#484456]">{r.topic}</td>
                        <td className="px-5 py-3.5">
                          <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold ${sensMap[r.sens]}`}>
                            {r.sens.replace(/_/g, " ")}
                          </span>
                        </td>
                        <td className="px-5 py-3.5">
                          <span className="inline-flex items-center gap-1.5 text-[12px] text-[#005a3e]">
                            <span className="material-symbols-outlined text-[14px]">{r.icon}</span>
                            {r.parse}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-[90px] bg-[#5317dd]">
        <div className="max-w-[700px] mx-auto px-8 text-center">
          <h2 className="text-[36px] md:text-[48px] font-bold text-white leading-tight mb-4">
            Documents speak.<br />Let DocVault AI translate.
          </h2>
          <p className="text-white/70 text-[16px] mb-8">Upload your first document in seconds. No signup required for the demo.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button onClick={() => router.push("/upload")}
              className="bg-white text-[#5317dd] px-8 py-3.5 rounded-lg font-bold text-[14px] hover:opacity-90 transition-all shadow-lg flex items-center gap-2 justify-center">
              <span className="material-symbols-outlined">upload_file</span>
              Upload Documents
            </button>
            <button onClick={() => router.push("/chat")}
              className="border-2 border-white/40 text-white px-8 py-3.5 rounded-lg font-bold text-[14px] hover:border-white/70 transition-all flex items-center gap-2 justify-center">
              <span className="material-symbols-outlined">chat</span>
              Ask DocVault AI
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#0d0d0d] text-white/50 py-8 text-center font-data-mono text-[12px]">
        <p>DocVault AI — Document Intelligence Platform · Built with Groq, ElevenLabs, ChromaDB, FastAPI, React</p>
        <p className="mt-1 text-white/30">Documents speak. DocVault AI translates.</p>
      </footer>
    </div>
  );
}
