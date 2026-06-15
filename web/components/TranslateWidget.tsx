"use client";

import React, { useEffect } from "react";

// Full-site translation via the free Google Translate Element. One dropdown
// translates every visible string into Hindi, Marathi, Gujarati, Tamil, Telugu,
// Bengali, Kannada, Malayalam, Punjabi, Urdu or back to English.
const LANGS = "en,hi,mr,gu,ta,te,bn,kn,ml,pa,ur";

export default function TranslateWidget() {
  useEffect(() => {
    const w = window as any;
    if (w.__gtInjected) return;
    w.__gtInjected = true;
    w.googleTranslateElementInit = () => {
      try {
        // eslint-disable-next-line no-new
        new w.google.translate.TranslateElement(
          {
            pageLanguage: "en",
            includedLanguages: LANGS,
            layout: w.google.translate.TranslateElement.InlineLayout.SIMPLE,
            autoDisplay: false,
          },
          "google_translate_element"
        );
      } catch { /* noop */ }
    };
    const s = document.createElement("script");
    s.src = "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";
    s.async = true;
    document.body.appendChild(s);
  }, []);

  return (
    <div className="flex items-center gap-1 text-gray-500" title="Translate this site">
      <span className="material-symbols-outlined text-[18px]">translate</span>
      <div id="google_translate_element" />
    </div>
  );
}
