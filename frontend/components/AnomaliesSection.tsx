"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Brain,
  ChevronDown,
  ChevronUp,
  Loader2,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { AnomalyReport, ExplainAnomalyResponse } from "@/types";
import { formatCurrency, explainAnomaly } from "@/lib/api";

interface AnomaliesSectionProps {
  report: AnomalyReport | null;
  sessionId?: string;
}

export const AnomaliesSection: React.FC<AnomaliesSectionProps> = ({
  report,
  sessionId,
}) => {
  const [explainingId, setExplainingId] = useState<string | null>(null);
  const [explanations, setExplanations] = useState<
    Record<string, ExplainAnomalyResponse>
  >({});
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({});

  const handleExplain = async (anomalyId: string) => {
    if (!sessionId) return;
    if (explanations[anomalyId]) {
      // Toggle
      setExpandedIds((prev) => ({ ...prev, [anomalyId]: !prev[anomalyId] }));
      return;
    }

    setExplainingId(anomalyId);
    try {
      const data = await explainAnomaly(sessionId, anomalyId);
      setExplanations((prev) => ({ ...prev, [anomalyId]: data }));
      setExpandedIds((prev) => ({ ...prev, [anomalyId]: true }));
    } catch {
      // fallback
    } finally {
      setExplainingId(null);
    }
  };

  if (!report || report.total_anomalies === 0) {
    return (
      <div className="bg-zinc-900/90 border border-zinc-800 p-5 rounded-2xl shadow-sm">
        <div className="flex items-center space-x-2.5">
          <div className="h-8 w-8 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-zinc-100">
              Unusual Transactions (0 Flagged)
            </h3>
            <p className="text-xs text-zinc-400 mt-0.5">
              All transactions conform to normal spending and category baselines within statistical bounds.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900/90 border border-zinc-800 p-5 sm:p-6 rounded-2xl shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            <h3 className="text-base font-bold text-zinc-100">
              Unusual Transactions ({report.total_anomalies} Detected)
            </h3>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Deterministic statistical detection: Leave-One-Out category baseline, IQR threshold &amp; budget share
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-950/80 text-amber-300 border border-amber-800/80 self-start sm:self-auto">
          Requires Review
        </span>
      </div>

      <div className="space-y-3">
        {report.anomalies.map((anom) => {
          const isExpanded = !!expandedIds[anom.id];
          const isExplaining = explainingId === anom.id;
          const expData = explanations[anom.id];

          return (
            <div
              key={anom.id}
              className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/70 hover:border-zinc-700/80 transition-all duration-200"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        anom.severity === "high"
                          ? "bg-rose-950/90 text-rose-300 border border-rose-800/70"
                          : "bg-amber-950/90 text-amber-300 border border-amber-800/70"
                      }`}
                    >
                      {anom.severity} Variance
                    </span>
                    <span className="text-xs text-zinc-400 font-mono">
                      {anom.date}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
                      {anom.category}
                    </span>
                  </div>

                  <p className="text-sm font-semibold text-zinc-100">
                    {anom.description}
                  </p>

                  <p className="text-xs text-amber-400/90 font-medium">
                    {anom.reason}
                  </p>
                </div>

                <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-2 shrink-0">
                  <div className="text-right">
                    <span className="text-base font-bold text-rose-400">
                      {formatCurrency(anom.amount)}
                    </span>
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                      {anom.type}
                    </p>
                  </div>

                  {sessionId && (
                    <button
                      onClick={() => handleExplain(anom.id)}
                      disabled={isExplaining}
                      className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-zinc-800 hover:bg-zinc-700 text-emerald-400 border border-zinc-700 transition cursor-pointer"
                    >
                      {isExplaining ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Brain className="h-3 w-3 text-emerald-400" />
                      )}
                      <span>{isExplaining ? "Explaining..." : isExpanded ? "Hide AI" : "Explain with AI"}</span>
                      {isExpanded ? (
                        <ChevronUp className="h-3 w-3" />
                      ) : (
                        <ChevronDown className="h-3 w-3" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {/* Inline AI Explanation Drawer */}
              {isExpanded && expData && (
                <div className="mt-3 pt-3 border-t border-zinc-800/80 animate-in fade-in duration-200 space-y-2 text-xs">
                  <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 leading-relaxed">
                    <p className="font-semibold text-emerald-400 mb-1 flex items-center space-x-1.5">
                      <Sparkles className="h-3.5 w-3.5" />
                      <span>Local AI Grounded Explanation:</span>
                    </p>
                    <p>{expData.ai_explanation}</p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-purple-950/30 border border-purple-900/40 text-purple-200 flex items-start space-x-2">
                    <ArrowRight className="h-3.5 w-3.5 text-purple-400 shrink-0 mt-0.5" />
                    <span>
                      <strong className="text-purple-300">Recommended Next Step: </strong>
                      {expData.recommended_action}
                    </span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
