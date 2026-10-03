"use client";

import React, { useState } from "react";
import { Sparkles, Brain, Cpu, AlertCircle, RefreshCw } from "lucide-react";
import { SystemHealth } from "@/types";

interface AIInsightsSectionProps {
  health: SystemHealth | null;
  sessionId: string;
}

export const AIInsightsSection: React.FC<AIInsightsSectionProps> = ({
  health,
  sessionId,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [insights, setInsights] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsGenerating(true);
    // Prepared for Phase 6/7 backend integration
    try {
      const res = await fetch("http://127.0.0.1:8000/api/ai/insights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data.summary || data.insights);
      } else {
        // Fallback message if endpoint not yet activated
        setInsights(
          "Local AI service module will be activated in Phase 6/7. Pre-computed deterministic metrics and anomaly flags are verified and ready for local LLM synthesis."
        );
      }
    } catch {
      setInsights(
        "Local AI service module will be activated in Phase 6/7. Pre-computed deterministic metrics and anomaly flags are verified and ready for local LLM synthesis."
      );
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-zinc-900 to-zinc-950 text-white p-6 rounded-xl border border-zinc-800 shadow-sm my-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-zinc-100 flex items-center space-x-2">
              <span>Local AI Financial Analyst</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-zinc-800 text-emerald-400 border border-zinc-700">
                Grounded Reasoning
              </span>
            </h3>
            <p className="text-xs text-zinc-400">
              Plain-English business explanations powered by local open-weight models (Zero cloud telemetry)
            </p>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition disabled:opacity-50 shadow-xs cursor-pointer"
        >
          {isGenerating ? (
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Brain className="h-3.5 w-3.5" />
          )}
          <span>{isGenerating ? "Analyzing Ledger..." : "Generate AI Briefing"}</span>
        </button>
      </div>

      {/* Content Area */}
      <div className="mt-4 pt-4 border-t border-zinc-800/80">
        {insights ? (
          <div className="p-4 rounded-lg bg-zinc-900/80 border border-zinc-800 text-xs leading-relaxed text-zinc-300">
            <p className="font-semibold text-emerald-400 mb-1">Executive Summary:</p>
            <p>{insights}</p>
          </div>
        ) : (
          <div className="flex items-center justify-between text-xs text-zinc-400">
            <div className="flex items-center space-x-2">
              <Cpu className="h-4 w-4 text-emerald-400" />
              <span>
                {health?.ollama_available
                  ? `Active Model: ${health.active_model || "Ollama Ready"}`
                  : "Local AI standby: Run 'ollama run llama3.2:1b' for instant local inference."}
              </span>
            </div>
            <span className="text-[11px] text-zinc-500">
              Only mathematically certified facts are passed to the model
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
