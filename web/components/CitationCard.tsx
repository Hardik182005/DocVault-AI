"use client";

import React, { useState } from "react";
import { api } from "@/lib/api";

export default function CitationCard({ citation }: { citation: any }) {
  const [modalOpen, setModalOpen] = useState(false);
  const imageUrl = api.getPageImageUrl(citation.doc_id, citation.page_number);

  return (
    <>
      {/* Thumbnail card */}
      <div
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-purple-50 border border-purple-200 cursor-pointer hover:bg-purple-100 transition-all group"
        onClick={() => setModalOpen(true)}
      >
        {/* Page thumbnail */}
        <div className="w-10 h-12 rounded overflow-hidden border border-purple-200 shrink-0 bg-gray-100">
          <img
            src={imageUrl}
            alt={`${citation.doc_name} p.${citation.page_number}`}
            className="w-full h-full object-cover"
            onError={e => { (e.target as HTMLImageElement).style.display = "none"; }}
          />
        </div>
        {/* Citation text */}
        <div>
          <p className="text-[11px] font-semibold text-purple-900 leading-tight">{citation.doc_name}</p>
          <p className="text-[11px] text-purple-700">Page {citation.page_number}</p>
          <span className="material-symbols-outlined text-[14px] text-purple-600 opacity-0 group-hover:opacity-100 transition-opacity">open_in_full</span>
        </div>
      </div>

      {/* Full-page modal */}
      {modalOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4"
          onClick={() => setModalOpen(false)}
        >
          <div
            className="bg-surface rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-auto"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant/30">
              <div>
                <p className="font-semibold text-on-surface text-[14px]">{citation.doc_name}</p>
                <p className="text-[12px] text-on-surface-variant">Page {citation.page_number}</p>
              </div>
              <button onClick={() => setModalOpen(false)}>
                <span className="material-symbols-outlined text-on-surface-variant">close</span>
              </button>
            </div>
            <div className="p-4">
              <img src={imageUrl} alt="Full page" className="w-full rounded-lg" />
              {citation.chunk_text && (
                <div className="mt-3 p-3 bg-surface-container rounded-lg">
                  <p className="text-[11px] font-semibold text-on-surface-variant mb-1">Extracted text from this page:</p>
                  <p className="text-[13px] text-on-surface">{citation.chunk_text}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
