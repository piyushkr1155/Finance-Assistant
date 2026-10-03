"use client";

import React from "react";
import { ShieldCheck, Cpu, HardDrive, RefreshCw } from "lucide-react";
import { SystemHealth } from "@/types";

interface HeaderProps {
  health: SystemHealth | null;
  onReset: () => void;
  hasData: boolean;
}

export const Header: React.FC<HeaderProps> = ({ health, onReset, hasData }) => {
  return (
    <header className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold text-xl shadow-sm">
            <HardDrive className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
                LocalLedger AI
              </h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                100% Local & Private
              </span>
            </div>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Understand your business finances with local AI.
            </p>
          </div>
        </div>

        {/* Status Indicators & Actions */}
        <div className="flex items-center space-x-3">
          {/* Privacy Badge */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Zero Cloud Exfiltration</span>
          </div>

          {/* Local AI Engine Status */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-xs border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900">
            <Cpu className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400" />
            <span className="text-zinc-700 dark:text-zinc-300">
              AI:{" "}
              {health?.ollama_available ? (
                <span className="font-medium text-emerald-600 dark:text-emerald-400">
                  {health.active_model || "Ollama Ready"}
                </span>
              ) : (
                <span className="text-amber-600 dark:text-amber-400">
                  Ollama Standby
                </span>
              )}
            </span>
          </div>

          {/* Reset / New File button */}
          {hasData && (
            <button
              onClick={onReset}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md text-zinc-700 bg-zinc-100 hover:bg-zinc-200 dark:text-zinc-300 dark:bg-zinc-800 dark:hover:bg-zinc-700 transition"
              title="Upload another ledger file"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Change File</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
