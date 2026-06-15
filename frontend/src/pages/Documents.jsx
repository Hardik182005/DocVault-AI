import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useSpeak, buildDocSpeech, buildLibrarySpeech } from "../lib/useSpeak";
import { redactPII } from "../lib/redact";

function Skeleton({ className = "" }) {
  return <div className={`animate-pulse bg-surface-container-high rounded ${className}`} />;
}

function SensitivityBadge({ level }) {
  const map = {
    public: "bg-green-100 text-green-700",
    internal: "bg-blue-100 text-blue-700",
    confidential: "bg-orange-100 text-orange-700",
    strictly_confidential: "bg-red-100 text-red-700",
  };
  const cls = map[(level || "").toLowerCase().replace(/ /g, "_")] || "bg-gray-100 text-gray-600";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold ${cls}`}>
      {level || "unknown"}
    </span>
  );
}

function TypeBadge({ type }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-surface-container text-on-surface-variant border border-outline-variant/30">
      {(type || "other").replace(/_/g, " ")}
    </span>
  );
}

function DocCard({ doc, onDelete, onOpen, speak, speakingId }) {
  const navigate = useNavigate();
  const cl = doc.classification || {};
  const isSpeaking = speakingId === doc.doc_id;
  const indexedDate = doc.indexed_at
    ? new Date(doc.indexed_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })
    : "—";

  return (
    <div className="glass-card rounded-xl card-inner-stroke p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
      {/* Icon + filename — click to open the document detail view */}
      <button
        type="button"
        onClick={() => onOpen(doc)}
        className="flex items-start gap-3 text-left group"
        title="Open document — view analysis and every page"
      >
        <span className="material-symbols-outlined text-primary text-2xl shrink-0" style={{ fontVariationSettings: "'FILL' 0" }}>description</span>
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-on-surface text-[13px] leading-tight truncate group-hover:text-primary transition-colors" title={doc.filename}>{doc.filename}</p>
          <p className="text-[10px] text-on-surface-variant mt-0.5">{doc.page_count ?? "?"} pages · {indexedDate}</p>
        </div>
        <span className="material-symbols-outlined text-on-surface-variant text-[18px] shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">open_in_full</span>
      </button>

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5">
        {cl.document_type && <TypeBadge type={cl.document_type} />}
        {cl.sensitivity_level && <SensitivityBadge level={cl.sensitivity_level} />}
        {cl.pii?.detected && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-100 text-red-700" title={`PII detected: ${(cl.pii.types || []).join(", ")}`}>
            <span className="material-symbols-outlined text-[12px]">privacy_tip</span>
            PII
          </span>
        )}
      </div>

      {/* Summary */}
      {cl.summary && (
        <p className="text-[12px] text-on-surface-variant line-clamp-2">{cl.summary}</p>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-auto pt-1">
        <button
          onClick={() => navigate("/chat")}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg bg-primary text-on-primary text-[12px] font-semibold hover:opacity-90 transition-opacity"
        >
          <span className="material-symbols-outlined text-[14px]">chat</span>
          Ask about this
        </button>
        {/* ElevenLabs speak — reads out the AI-extracted analysis of this doc */}
        <button
          onClick={() => speak(buildDocSpeech(doc), doc.doc_id)}
          className={`w-9 h-9 flex items-center justify-center rounded-lg transition-colors ${
            isSpeaking ? "bg-primary text-on-primary animate-pulse" : "bg-secondary/10 text-secondary hover:bg-secondary/20"
          }`}
          title={isSpeaking ? "Stop" : "Listen to this document's analysis"}
        >
          <span className="material-symbols-outlined text-[16px]">{isSpeaking ? "stop_circle" : "volume_up"}</span>
        </button>
        <button
          onClick={() => onDelete(doc.doc_id)}
          className="w-9 h-9 flex items-center justify-center rounded-lg bg-error/10 text-error hover:bg-error/20 transition-colors"
          title="Delete document"
        >
          <span className="material-symbols-outlined text-[16px]">delete</span>
        </button>
      </div>
    </div>
  );
}

// Full-screen document detail — analysis + every rendered page (page 1, 2, …).
function DocDetailModal({ doc, onClose, speak, speakingId }) {
  const [zoomPage, setZoomPage] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(true);
  const [redact, setRedact] = useState(!!doc.classification?.pii?.detected); // default on when PII present

  // Fetch the full document (includes per-page extracted text + tables).
  useEffect(() => {
    let active = true;
    setLoadingDetail(true);
    api.getDocument(doc.doc_id)
      .then(d => { if (active) setDetail(d); })
      .catch(() => {})
      .finally(() => { if (active) setLoadingDetail(false); });
    return () => { active = false; };
  }, [doc.doc_id]);

  if (!doc) return null;
  const cl = doc.classification || {};
  const pageCount = doc.page_count || 1;
  const pages = Array.from({ length: pageCount }, (_, i) => i + 1);
  const cc = cl.content_characteristics || {};
  const speakId = `detail-${doc.doc_id}`;
  const extractedPages = detail?.pages || [];

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div
        className="bg-surface rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <span className="material-symbols-outlined text-primary text-2xl shrink-0">description</span>
            <div className="min-w-0">
              <p className="font-semibold text-on-surface text-[15px] truncate" title={doc.filename}>{doc.filename}</p>
              <p className="text-[11px] text-on-surface-variant">{pageCount} page{pageCount > 1 ? "s" : ""} · {(cl.document_type || "document").replace(/_/g, " ")}</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => speak(buildDocSpeech(doc), speakId)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-semibold transition-colors ${
                speakingId === speakId ? "bg-primary text-on-primary animate-pulse" : "bg-secondary/10 text-secondary hover:bg-secondary/20"
              }`}
              title="Listen to the analysis"
            >
              <span className="material-symbols-outlined text-[16px]">{speakingId === speakId ? "stop_circle" : "volume_up"}</span>
              {speakingId === speakId ? "Stop" : "Listen"}
            </button>
            <button onClick={onClose} className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-surface-container-high" title="Close">
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="overflow-y-auto p-6 space-y-6">
          {/* Analysis */}
          <section>
            <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-2 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[18px]">psychology</span>
              AI ANALYSIS
            </h3>
            <div className="glass-card rounded-xl card-inner-stroke p-4 space-y-3">
              {cl.summary && <p className="text-[13px] text-on-surface leading-relaxed">{cl.summary}</p>}
              <div className="flex flex-wrap gap-1.5">
                {cl.document_type && <TypeBadge type={cl.document_type} />}
                {cl.sensitivity_level && <SensitivityBadge level={cl.sensitivity_level} />}
                {cl.language && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-surface-container text-on-surface-variant border border-outline-variant/30">{cl.language}</span>}
              </div>
              {cl.sensitivity_reason && (
                <p className="text-[12px] text-on-surface-variant"><span className="font-semibold">Why sensitive:</span> {cl.sensitivity_reason}</p>
              )}
              {cl.pii?.detected && (
                <div className="flex items-start gap-2 p-2.5 rounded-lg bg-red-50 border border-red-200">
                  <span className="material-symbols-outlined text-red-600 text-[18px] shrink-0">privacy_tip</span>
                  <div>
                    <p className="text-[12px] font-semibold text-red-700">PII detected</p>
                    <p className="text-[11px] text-red-600">{(cl.pii.types || []).join(", ")}</p>
                  </div>
                </div>
              )}
              {Array.isArray(cl.key_entities) && cl.key_entities.length > 0 && (
                <div className="text-[12px] text-on-surface-variant">
                  <span className="font-semibold">Key entities:</span> {cl.key_entities.join(", ")}
                </div>
              )}
              {Array.isArray(cl.tags) && cl.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {cl.tags.map((t, i) => (
                    <span key={i} className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-primary/10 text-primary">#{t}</span>
                  ))}
                </div>
              )}
              <div className="flex flex-wrap gap-3 text-[11px] text-on-surface-variant pt-1">
                {cc.has_tables && <span className="flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">table</span>Tables</span>}
                {cc.has_handwriting && <span className="flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">draw</span>Handwriting</span>}
                {cc.is_scanned && <span className="flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">scanner</span>Scanned</span>}
                {cc.has_images && <span className="flex items-center gap-1"><span className="material-symbols-outlined text-[14px]">image</span>Images</span>}
              </div>
            </div>
          </section>

          {/* Pages */}
          <section>
            <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[18px]">collections</span>
              PAGES ({pageCount})
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {pages.map(n => (
                <button
                  key={n}
                  type="button"
                  onClick={() => setZoomPage(n)}
                  className="group relative rounded-lg overflow-hidden border border-outline-variant/40 hover:border-primary transition-colors bg-white"
                  title={`Open page ${n}`}
                >
                  <img
                    src={api.getPageImageUrl(doc.doc_id, n)}
                    alt={`Page ${n}`}
                    loading="lazy"
                    className="w-full h-44 object-cover object-top"
                  />
                  <span className="absolute bottom-0 inset-x-0 bg-black/60 text-white text-[11px] font-semibold py-1 text-center">
                    Page {n}
                  </span>
                </button>
              ))}
            </div>
          </section>

          {/* Extracted content — the actual parsed text per page */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-label-caps text-label-caps text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">article</span>
                EXTRACTED CONTENT {extractedPages.length > 0 && `(${extractedPages.length} PAGES)`}
              </h3>
              {/* PII Redaction toggle — masks sensitive values in the text below */}
              <button
                onClick={() => setRedact(r => !r)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold transition-colors ${
                  redact ? "bg-red-600 text-white" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
                }`}
                title="Mask emails, phone numbers, cards and IDs"
              >
                <span className="material-symbols-outlined text-[14px]">{redact ? "visibility_off" : "visibility"}</span>
                {redact ? "PII Redacted" : "Show PII"}
              </button>
            </div>
            {loadingDetail ? (
              <p className="text-[12px] text-on-surface-variant">Loading extracted text…</p>
            ) : extractedPages.length === 0 ? (
              <p className="text-[12px] text-on-surface-variant">No extracted text available for this document.</p>
            ) : (
              <div className="space-y-3">
                {extractedPages.map((p) => (
                  <div key={p.page_number} className="glass-card rounded-xl card-inner-stroke overflow-hidden">
                    <div className="flex items-center gap-2 px-4 py-2 border-b border-outline-variant/30 bg-surface-container-low">
                      <span className="text-[12px] font-semibold text-on-surface">Page {p.page_number}</span>
                      {p.table_count > 0 && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                          <span className="material-symbols-outlined text-[12px]">table</span>
                          {p.table_count} table{p.table_count > 1 ? "s" : ""}
                        </span>
                      )}
                    </div>
                    <pre className="px-4 py-3 text-[12px] text-on-surface whitespace-pre-wrap font-data-mono max-h-56 overflow-y-auto leading-relaxed">
                      {(redact ? redactPII(p.text) : p.text)?.trim() || "(no text extracted on this page)"}
                    </pre>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      {/* Single-page zoom */}
      {zoomPage && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-black/80" onClick={() => setZoomPage(null)}>
          <div className="relative max-w-3xl max-h-[92vh]" onClick={e => e.stopPropagation()}>
            <img src={api.getPageImageUrl(doc.doc_id, zoomPage)} alt={`Page ${zoomPage}`} className="max-h-[92vh] w-auto rounded-lg shadow-2xl" />
            <span className="absolute top-2 left-2 bg-black/70 text-white text-[12px] font-semibold px-2 py-1 rounded">Page {zoomPage} / {pageCount}</span>
            <button onClick={() => setZoomPage(null)} className="absolute top-2 right-2 w-9 h-9 flex items-center justify-center rounded-lg bg-black/70 text-white hover:bg-black">
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all");
  const { speak, speakingId } = useSpeak();
  const [briefing, setBriefing] = useState(null);
  const [briefingLoading, setBriefingLoading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);

  // AI Audio Briefing — the standout feature. Asks the backend to synthesize a
  // spoken executive briefing across the whole vault, then narrates it via
  // ElevenLabs. Security-aware: it flags confidential documents.
  const playBriefing = async () => {
    if (speakingId === "briefing") { speak("", "briefing"); return; } // toggles stop
    setBriefingLoading(true);
    try {
      const data = await api.getBriefing();
      const text = data?.briefing || buildLibrarySpeech(docs);
      setBriefing(text);
      speak(text, "briefing");
    } catch {
      const text = buildLibrarySpeech(docs);
      setBriefing(text);
      speak(text, "briefing");
    } finally {
      setBriefingLoading(false);
    }
  };

  useEffect(() => {
    let active = true;
    api.getDocuments()
      .then(d => { if (active && Array.isArray(d)) setDocs(d); })
      .catch(() => {})
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const handleDelete = async (docId) => {
    if (!window.confirm("Delete this document? This cannot be undone.")) return;
    try {
      await api.deleteDocument(docId);
      setDocs(prev => prev.filter(d => d.doc_id !== docId));
    } catch {
      alert("Failed to delete document. Please try again.");
    }
  };

  // Group by document_type
  const byType = docs.reduce((acc, doc) => {
    const type = doc.classification?.document_type || "other";
    if (!acc[type]) acc[type] = [];
    acc[type].push(doc);
    return acc;
  }, {});

  return (
    <div className="p-gutter max-w-container-max mx-auto w-full">
      {/* Header */}
      <div className="mb-6 glass-card p-6 rounded-xl card-inner-stroke flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary text-3xl">folder_open</span>
          <div>
            <h2 className="font-headline-lg text-title-lg font-bold text-on-surface tracking-tight">My Documents</h2>
            <p className="font-body-md text-body-md text-on-surface-variant">
              {loading ? "Loading…" : `${docs.length} document${docs.length === 1 ? "" : "s"} indexed`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Announce the library — ElevenLabs reads out which documents exist */}
          <button
            onClick={() => speak(buildLibrarySpeech(docs), "library")}
            disabled={loading}
            className={`inline-flex items-center gap-1.5 text-[12px] font-semibold px-3 py-2 rounded-lg transition-colors disabled:opacity-40 ${
              speakingId === "library" ? "bg-primary text-on-primary animate-pulse" : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
            }`}
            title="Hear which documents are in your knowledge base"
          >
            <span className="material-symbols-outlined text-[16px]">{speakingId === "library" ? "stop_circle" : "campaign"}</span>
            {speakingId === "library" ? "Stop" : "Announce"}
          </button>
          {/* AI Audio Briefing — the standout feature */}
          <button
            onClick={playBriefing}
            disabled={loading || briefingLoading}
            className={`inline-flex items-center gap-1.5 text-[12px] font-semibold px-3 py-2 rounded-lg transition-colors disabled:opacity-40 ${
              speakingId === "briefing" ? "bg-primary text-on-primary animate-pulse" : "bg-gradient-to-r from-primary to-secondary text-on-primary hover:opacity-90"
            }`}
            title="Generate & narrate an AI executive briefing of your whole vault"
          >
            <span className="material-symbols-outlined text-[16px]">
              {briefingLoading ? "progress_activity" : speakingId === "briefing" ? "stop_circle" : "auto_awesome"}
            </span>
            {briefingLoading ? "Generating…" : speakingId === "briefing" ? "Stop" : "AI Audio Briefing"}
          </button>
          <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-full bg-purple-50 text-purple-700">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
            {docs.length} indexed
          </span>
        </div>
      </div>

      {/* Briefing transcript — shows what the voice is narrating */}
      {briefing && (
        <div className="mb-6 glass-card p-5 rounded-xl card-inner-stroke border-l-4 border-primary">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-primary text-[18px]">graphic_eq</span>
            <span className="font-label-caps text-label-caps text-on-surface-variant">AI AUDIO BRIEFING — TRANSCRIPT</span>
          </div>
          <p className="text-[13px] text-on-surface leading-relaxed">{briefing}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-outline-variant/30">
        {[
          { id: "all", label: "All Documents" },
          { id: "bytype", label: "By Type" },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-[13px] font-semibold transition-all border-b-2 -mb-px ${
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loading skeletons */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-gutter">
          {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-52" />)}
        </div>
      )}

      {/* Tab: All Documents */}
      {!loading && activeTab === "all" && (
        docs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4 text-on-surface-variant">
            <span className="material-symbols-outlined text-5xl opacity-30">folder_open</span>
            <p className="text-[15px] font-medium">No documents yet</p>
            <p className="text-[13px]">Upload some files to get started.</p>
            <a href="/upload" className="mt-2 px-5 py-2.5 bg-primary text-on-primary rounded-lg text-[13px] font-semibold hover:opacity-90">
              Upload Documents
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-gutter">
            {docs.map(doc => (
              <DocCard key={doc.doc_id} doc={doc} onDelete={handleDelete} onOpen={setSelectedDoc} speak={speak} speakingId={speakingId} />
            ))}
          </div>
        )
      )}

      {/* Tab: By Type */}
      {!loading && activeTab === "bytype" && (
        Object.keys(byType).length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4 text-on-surface-variant">
            <span className="material-symbols-outlined text-5xl opacity-30">category</span>
            <p className="text-[15px] font-medium">No documents yet</p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(byType).map(([type, typeDocs]) => (
              <section key={type}>
                <div className="flex items-center gap-3 mb-4">
                  <span className="material-symbols-outlined text-secondary text-lg">label</span>
                  <h3 className="font-title-md text-on-surface font-semibold capitalize">{type.replace(/_/g, " ")}</h3>
                  <span className="text-[11px] text-on-surface-variant">({typeDocs.length})</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-gutter">
                  {typeDocs.map(doc => (
                    <DocCard key={doc.doc_id} doc={doc} onDelete={handleDelete} onOpen={setSelectedDoc} speak={speak} speakingId={speakingId} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        )
      )}

      {/* Document detail view — analysis + every page */}
      {selectedDoc && (
        <DocDetailModal
          doc={selectedDoc}
          onClose={() => setSelectedDoc(null)}
          speak={speak}
          speakingId={speakingId}
        />
      )}
    </div>
  );
}
