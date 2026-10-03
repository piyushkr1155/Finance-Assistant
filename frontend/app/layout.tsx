import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "LocalLedger AI — Privacy-First Business Financial Intelligence",
  description:
    "An open-source, local-first financial intelligence assistant for small businesses. Deterministic analytics, cash flow trends, and grounded local AI via Ollama. 100% on-device, zero cloud data exfiltration.",
  keywords: [
    "small business finance",
    "local ai",
    "privacy ledger",
    "cash flow analytics",
    "ollama",
    "hacktoberfest 2026",
    "open source accounting",
  ],
  authors: [{ name: "LocalLedger AI Contributors" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-zinc-950 text-zinc-100 selection:bg-emerald-500/30 selection:text-emerald-200">
        {children}
      </body>
    </html>
  );
}
