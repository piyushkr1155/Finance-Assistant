"use client";

import React, { useState } from "react";
import { ShieldCheck, Cpu, HardDrive, RefreshCw, Lock, ExternalLink, X } from "lucide-react";
import { SystemHealth } from "@/types";

interface HeaderProps {
  health: SystemHealth | null;
  onReset: () => void;
  hasData: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, onReset, hasData }) => {
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);

  return (
    <>
      <header className="border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-30 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white font-bold shadow-md shadow-emerald-950/40">
              <HardDrive className="h-4.5 w-4.5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-base font-bold tracking-tight text-zinc-100">
                  LocalLedger AI
                </h1>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                  100% Local
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 hidden sm:block">
                Privacy-first financial intelligence powered by local open-weight AI.
              </p>
            </div>
          </div>

          {/* Status Indicators & Actions */}
          <div className="flex items-center space-x-2.5">
            {/* Privacy Guarantee Pill */}
            <button
              onClick={() => setShowPrivacyModal(true)}
              className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-zinc-900 hover:bg-zinc-850 text-zinc-300 border border-zinc-800 transition cursor-pointer"
              title="Click to view Privacy & Security Architecture"
            >
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
              <span className="hidden md:inline">Zero Cloud Exfiltration</span>
              <span className="md:hidden">Privacy</span>
            </button>

            {/* Local AI Engine Status Pill */}
            <div
              className={`flex items-center space-x-2 px-2.5 py-1.5 rounded-lg text-xs font-medium border ${
                health?.ollama_available
                  ? "bg-zinc-900 border-zinc-800 text-zinc-300"
                  : "bg-amber-950/20 border-amber-800/40 text-amber-300"
              }`}
            >
              <div className="relative flex h-2 w-2">
                {health?.ollama_available && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                )}
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    health?.ollama_available ? "bg-emerald-500" : "bg-amber-500"
                  }`}
                ></span>
              </div>
              <Cpu className="h-3.5 w-3.5 text-zinc-400" />
              <span className="text-zinc-300">
                {health?.ollama_available ? (
                  <span className="font-semibold text-emerald-400">
                    {health.active_model || "Ollama Ready"}
                  </span>
                ) : (
                  <span>Ollama Standby</span>
                )}
              </span>
            </div>

            {/* Change / Purge File Button */}
            {hasData && (
              <button
                onClick={onReset}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg text-rose-300 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/50 transition cursor-pointer"
                title="Purge session memory and upload a new ledger file"
              >
                <RefreshCw className="h-3.5 w-3.5 text-rose-400" />
                <span>Purge & Reset</span>
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Privacy Architecture Modal */}
      {showPrivacyModal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
        >
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowPrivacyModal(false)}
              className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-100 p-1 rounded-lg transition"
              aria-label="Close modal"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="flex items-center space-x-3 mb-4">
              <div className="h-10 w-10 rounded-xl bg-emerald-950/80 border border-emerald-800 flex items-center justify-center text-emerald-400">
                <Lock className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-zinc-100">
                  Privacy & Data Architecture
                </h3>
                <p className="text-xs text-zinc-400">
                  Open-source, local-first guarantees
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs text-zinc-300 leading-relaxed">
              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                <p className="font-semibold text-emerald-400 mb-0.5">
                  1. Zero Cloud Exfiltration
                </p>
                <p className="text-zinc-400">
                  Financial figures are never sent to OpenAI, Anthropic, Google, or any remote server. Analysis executes 100% on your machine.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                <p className="font-semibold text-blue-400 mb-0.5">
                  2. In-Memory Session Storage
                </p>
                <p className="text-zinc-400">
                  Transactions exist only in server memory for the duration of your session. Clicking &ldquo;Purge &amp; Reset&rdquo; instantly erases the active ledger.
                </p>
              </div>

              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
                <p className="font-semibold text-purple-400 mb-0.5">
                  3. Deterministic Grounding
                </p>
                <p className="text-zinc-400">
                  Totals and trends are computed via deterministic Python algorithms with zero hallucinations. The local LLM receives only certified math context.
                </p>
              </div>
            </div>

            <div className="mt-5 pt-4 border-t border-zinc-800 flex justify-end">
              <button
                onClick={() => setShowPrivacyModal(false)}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition cursor-pointer"
              >
                Understood
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
