import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DocVault AI - Document Intelligence Platform",
  description:
    "Upload scanned PDFs, handwritten notes, and messy reports. Ask anything. Get grounded answers with exact source citations. Documents speak. DocVault AI translates.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="light">
      <head>
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400..700;1,400..700&family=JetBrains+Mono:wght@400;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background text-on-background min-h-screen overflow-x-hidden font-body-md text-body-md">
        {children}
      </body>
    </html>
  );
}
