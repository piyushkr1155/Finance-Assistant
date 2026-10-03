"use client";

import React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import { AnomalyReport } from "@/types";
import { formatCurrency } from "@/lib/api";

interface AnomaliesSectionProps {
  report: AnomalyReport | null;
}

export const AnomaliesSection: React.FC<AnomaliesSectionProps> = ({ report }) => {
  if (!report || report.total_anomalies === 0) {
    return (
      <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
        <div className="flex items-center space-x-2">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Unusual Transactions (0 Flagged)
          </h3>
        </div>
        <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
          All transactions conform to normal spending and category baselines within statistical bounds.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
              Unusual Transactions ({report.total_anomalies} Detected)
            </h3>
          </div>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
            Deterministic statistical outlier detection based on category multiples and IQR thresholds
          </p>
        </div>
        <span className="px-2.5 py-1 rounded text-xs font-semibold bg-amber-50 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          Requires Review
        </span>
      </div>

      <div className="mt-4 space-y-3">
        {report.anomalies.map((anom) => (
          <div
            key={anom.id}
            className="p-3.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    anom.severity === "high"
                      ? "bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300"
                      : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                  }`}
                >
                  {anom.severity} Variance
                </span>
                <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
                  {anom.date}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                  {anom.category}
                </span>
              </div>
              <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                {anom.description}
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-400 font-medium">
                {anom.reason}
              </p>
            </div>

            <div className="text-right flex-shrink-0">
              <span className="text-base font-bold text-rose-600 dark:text-rose-400">
                {formatCurrency(anom.amount)}
              </span>
              <p className="text-[11px] text-zinc-400 capitalize">{anom.type}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
