"use client";

import React, { useState } from "react";
import {
  MessageSquare,
  Send,
  Sparkles,
  HelpCircle,
  CheckCircle2,
  AlertCircle,
  Lightbulb,
  ArrowRight,
  Loader2,
} from "lucide-react";
import { AskBusinessResponse } from "@/types";
import { askBusiness } from "@/lib/api";

interface AskMyBusinessProps {
  sessionId: string;
}

const PRESET_PROMPTS = [
  "Why did expenses increase this month?",
  "What are my biggest expense categories?",
  "Which transactions look unusual?",
  "How is my net cash flow and savings margin?",
  "What should I investigate first?",
];

export const AskMyBusinessSection: React.FC<AskMyBusinessProps> = ({
  sessionId,
}) => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AskBusinessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const executeAsk = async (textToAsk: string) => {
    const trimmed = textToAsk.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await askBusiness(sessionId, trimmed);
      setResponse(data);
    } catch (err: any) {
      setError(err.message || "Failed to process question.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    executeAsk(query);
  };

  const handleChipClick = (promptText: string) => {
    setQuery(promptText);
    executeAsk(promptText);
  };

  return (
    <div className="bg-zinc-900/90 border border-zinc-800 p-6 rounded-2xl shadow-md my-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <MessageSquare className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-zinc-100 flex items-center space-x-2">
              <span>Ask My Business</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-blue-950/80 text-blue-400 border border-blue-800/60">
                Deterministic Q&amp;A
              </span>
            </h3>
            <p className="text-xs text-zinc-400">
              Query revenue, expenses, trends, or unusual items with mathematical precision
            </p>
          </div>
        </div>

        <span className="text-[11px] text-zinc-500 hidden sm:inline-block">
          Zero Hallucination Guarantee
        </span>
      </div>

      {/* Preset Quick Chips */}
      <div className="mb-4">
        <p className="text-[11px] font-medium text-zinc-400 mb-2 flex items-center space-x-1">
          <Sparkles className="h-3 w-3 text-amber-400" />
          <span>Suggested Business Inquiries:</span>
        </p>
        <div className="flex flex-wrap gap-2">
          {PRESET_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleChipClick(p)}
              disabled={isLoading}
              className="text-xs px-3 py-1.5 rounded-lg bg-zinc-950 hover:bg-zinc-800 text-zinc-300 hover:text-zinc-100 border border-zinc-800 transition active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSubmit} className="relative flex items-center mb-5">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your finances (e.g. 'What was my highest expense?')..."
          disabled={isLoading}
          className="w-full pl-4 pr-24 py-3 rounded-xl bg-zinc-950 border border-zinc-800 text-xs sm:text-sm text-zinc-100 placeholder-zinc-500 focus:outline-hidden focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition shadow-inner"
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading}
          className="absolute right-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition disabled:opacity-40 cursor-pointer flex items-center space-x-1.5"
        >
          {isLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Send className="h-3.5 w-3.5" />
          )}
          <span>{isLoading ? "Thinking..." : "Ask"}</span>
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 mb-4">
          {error}
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="p-5 rounded-xl bg-zinc-950/80 border border-zinc-800 animate-pulse space-y-3">
          <div className="h-4 bg-zinc-800 rounded w-1/4"></div>
          <div className="h-4 bg-zinc-800 rounded w-3/4"></div>
          <div className="h-4 bg-zinc-800 rounded w-1/2"></div>
        </div>
      )}

      {/* Structured 4-Card Response */}
      {response && !isLoading && (
        <div className="space-y-4 pt-2 animate-in fade-in duration-200">
          {/* Query & Intent Pill */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-1 border-b border-zinc-800/80">
            <span className="text-xs font-semibold text-zinc-300">
              Q: &ldquo;{response.query}&rdquo;
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded font-mono font-semibold bg-zinc-800 text-emerald-400 border border-zinc-700">
              Intent: {response.intent}
            </span>
          </div>

          {/* 1. Direct Grounded Answer */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/90">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1 flex items-center space-x-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              <span>Grounded Answer</span>
            </h4>
            <p className="text-xs leading-relaxed text-zinc-200">
              {response.answer}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 2. Key Data Points */}
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/90">
              <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <HelpCircle className="h-3.5 w-3.5 text-blue-400" />
                <span>Key Certified Data</span>
              </h4>
              <ul className="space-y-1.5 text-xs text-zinc-300">
                {response.key_data.map((item, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-blue-400 shrink-0">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* 3. Why It Matters */}
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/90">
              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
                <span>Why It Matters</span>
              </h4>
              <p className="text-xs text-zinc-300 leading-relaxed">
                {response.why_it_matters}
              </p>
            </div>

            {/* 4. What To Check */}
            <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800/90">
              <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <ArrowRight className="h-3.5 w-3.5 text-purple-400" />
                <span>Recommended Action</span>
              </h4>
              <ul className="space-y-1.5 text-xs text-zinc-300">
                {response.what_to_check.map((item, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-purple-400 shrink-0">→</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
