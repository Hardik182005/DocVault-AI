"use client";

import React, { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import TranslateWidget from "./TranslateWidget";

const BREADCRUMBS: Record<string, string[]> = {
  "/chat":      ["DocVault AI", "Ask DocVault AI"],
  "/upload":    ["DocVault AI", "Upload Documents"],
  "/documents": ["DocVault AI", "My Documents"],
  "/settings":  ["DocVault AI", "Settings"],
};

function getBreadcrumb(pathname: string) {
  return BREADCRUMBS[pathname] || ["DocVault AI"];
}

export default function TopNavBar({ onToggleMobileMenu }: { onToggleMobileMenu: () => void }) {
  const router = useRouter();
  const pathname = usePathname();
  const [query, setQuery] = useState("");
  const [prefs, setPrefs] = useState({ name: "User" });

  const crumbs = getBreadcrumb(pathname);

  useEffect(() => {
    try {
      const p = JSON.parse(localStorage.getItem("bfai_prefs") || "{}");
      if (p.name) setPrefs(p);
    } catch { /* ignore */ }
  }, []);

  const initial = (prefs.name || "U").charAt(0).toUpperCase();

  return (
    <header className="bg-white h-[60px] flex items-center px-6 gap-4 sticky top-0 z-30" style={{ borderBottom: "1px solid #e5e7eb" }}>

      {/* Mobile hamburger */}
      <button onClick={onToggleMobileMenu} className="md:hidden text-gray-500 hover:text-gray-800 mr-1">
        <span className="material-symbols-outlined">menu</span>
      </button>

      {/* Breadcrumb */}
      <div className="hidden md:flex items-center gap-1.5 text-[13px] text-gray-400 shrink-0">
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span className="text-gray-300">›</span>}
            <span className={i === crumbs.length - 1 ? "text-gray-700 font-semibold" : "text-gray-400"}>{c}</span>
          </React.Fragment>
        ))}
      </div>

      {/* Center search */}
      <div className="flex-1 max-w-[480px] mx-auto relative">
        <div className="relative">
          <input
            type="text"
            placeholder="Search documents..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="w-[200px] md:w-[280px] px-3 py-2 rounded-lg bg-gray-50 text-[13px] text-gray-800 placeholder:text-gray-400 border border-gray-200 focus:outline-none focus:border-[#6434ed]/50"
          />
          <span className="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 text-[18px] text-gray-400">search</span>
        </div>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Full-site language translator */}
        <div className="hidden sm:block"><TranslateWidget /></div>
        <button className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <span className="material-symbols-outlined text-[20px]">notifications</span>
        </button>
        <button onClick={() => router.push("/settings")} className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <span className="material-symbols-outlined text-[20px]">help_outline</span>
        </button>
        <button onClick={() => router.push("/settings")}
          className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors ml-1">
          <div className="w-6 h-6 rounded-full bg-[#6434ed] flex items-center justify-center text-white text-[11px] font-bold">
            {initial}
          </div>
        </button>
      </div>
    </header>
  );
}
