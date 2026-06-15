import React, { useEffect } from "react";

// Full-site translation via the free Google Translate Element. One dropdown
// translates every visible string into Hindi, Marathi, Gujarati, Tamil, Telugu,
// Bengali, Kannada, Malayalam, Punjabi, Urdu or back to English — no per-string
// i18n wiring needed, and it covers content rendered from the documents too.
const LANGS = "en,hi,mr,gu,ta,te,bn,kn,ml,pa,ur";

export default function TranslateWidget() {
  useEffect(() => {
    if (window.__gtInjected) return;
    window.__gtInjected = true;
    window.googleTranslateElementInit = () => {
      try {
        // eslint-disable-next-line no-new
        new window.google.translate.TranslateElement(
          {
            pageLanguage: "en",
            includedLanguages: LANGS,
            layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE,
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
