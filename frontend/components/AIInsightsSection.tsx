"use client";

import React, { useState } from "react";
import { Sparkles, Brain, Cpu, RefreshCw, Copy, Check, Info } from "lucide-react";
import { SystemHealth, AIGenerateResponse } from "@/types";
import { generateAIInsights } from "@/lib/api";

interface AIInsightsSectionProps {
  health: SystemHealth | null;
  sessionId: string;
}

export const AIInsightsSection: React.FC<AIInsightsSectionProps> = ({
  health,
  sessionId,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [insightsData, setInsightsData] = useState<AIGenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const data = await generateAIInsights(sessionId);
      setInsightsData(data);
    } catch (err: any) {
      setError(err.message || "Failed to generate AI insights.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    if (!insightsData?.response) return;
    navigator.clipboard.writeText(insightsData.response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gradient-to-br from-zinc-900 via-zinc-900/95 to-zinc-950 text-white p-6 rounded-2xl border border-zinc-800 shadow-md my-6 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10">
        <div className="flex items-center space-x-3.5">
          <div className="h-11 w-11 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-inner">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-base font-bold text-zinc-100">
                Local AI Financial Analyst
              </h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-zinc-800 text-emerald-400 border border-zinc-700">
                Grounded Math
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Natural-language executive narrative synthesized by your local open-weight LLM
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {insightsData && (
            <button
              onClick={handleCopy}
              className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition cursor-pointer"
              title="Copy executive briefing to clipboard"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>
          )}

          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 active:scale-95 text-white transition disabled:opacity-50 shadow-sm cursor-pointer"
          >
            {isGenerating ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Brain className="h-3.5 w-3.5" />
            )}
            <span>
              {isGenerating
                ? "Synthesizing Briefing..."
                : insightsData
                ? "Re-Analyze Ledger"
                : "Generate Executive Briefing"}
            </span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="mt-5 pt-4 border-t border-zinc-800/80 relative z-10">
        {error && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 mb-3">
            {error}
          </div>
        )}

        {insightsData ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-[11px] text-zinc-400 pb-1">
              <span className="flex items-center space-x-1.5">
                <Cpu className="h-3.5 w-3.5 text-emerald-400" />
                <span>
                  Model:{" "}
                  <strong className="text-zinc-200">
                    {insightsData.model_used || "Local Intelligence"}
                  </strong>
                </span>
                {insightsData.is_fallback && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-950/60 text-amber-300 border border-amber-800/60">
                    Deterministic Fallback
                  </span>
                )}
              </span>
              <span className="text-zinc-500">
                100% Certified Numerical Facts
              </span>
            </div>

            <div className="p-4.5 rounded-xl bg-zinc-950/70 border border-zinc-800/80 text-xs leading-relaxed text-zinc-200 whitespace-pre-line font-normal">
              {insightsData.response}
            </div>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-zinc-400">
            <div className="flex items-center space-x-2">
              <Cpu className="h-4 w-4 text-emerald-400 shrink-0" />
              <span>
                {health?.ollama_available
                  ? `Local LLM ready on Ollama (${health.active_model}). Click "Generate Executive Briefing" to run.`
                  : "Ollama standby: Run 'ollama run llama3.2:1b' locally for high-speed offline reasoning."}
              </span>
            </div>
            <div className="flex items-center space-x-1 text-[11px] text-zinc-500">
              <Info className="h-3.5 w-3.5 shrink-0" />
              <span>Grounded in deterministic calculations</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
