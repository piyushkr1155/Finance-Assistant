"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { UploadZone } from "@/components/UploadZone";
import { KPICards } from "@/components/KPICards";
import { CashFlowChart } from "@/components/CashFlowChart";
import { CategoryChart } from "@/components/CategoryChart";
import { AnomaliesSection } from "@/components/AnomaliesSection";
import { LargestExpensesSection } from "@/components/LargestExpensesSection";
import { AIInsightsSection } from "@/components/AIInsightsSection";
import { AskMyBusinessSection } from "@/components/AskMyBusinessSection";
import { TransactionsTable } from "@/components/TransactionsTable";

import {
  UploadResult,
  SummaryKPIs,
  MonthlyMetric,
  CategoryBreakdown,
  LargestTransaction,
  AnomalyReport,
  Transaction,
  SystemHealth,
} from "@/types";

import {
  checkHealth,
  uploadFinancialFile,
  fetchSummary,
  fetchMonthlyTrends,
  fetchCategoryBreakdown,
  fetchLargestTransactions,
  fetchAnomalies,
  fetchTransactions,
  purgeSession,
} from "@/lib/api";

import { FileSpreadsheet, CheckCircle2, Shield, Loader2, Sparkles, AlertCircle } from "lucide-react";

export default function Dashboard() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Active Session State
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [summary, setSummary] = useState<SummaryKPIs | null>(null);
  const [monthlyTrends, setMonthlyTrends] = useState<MonthlyMetric[]>([]);
  const [categories, setCategories] = useState<CategoryBreakdown[]>([]);
  const [largestTxns, setLargestTxns] = useState<LargestTransaction[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyReport | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [totalTxnCount, setTotalTxnCount] = useState(0);

  // 1. Initial Health Check
  useEffect(() => {
    checkHealth()
      .then((data) => setHealth(data))
      .catch(() => {
        setHealth(null);
      });
  }, []);

  // 2. Load all analytical data once a session is established
  const loadDashboardData = async (sessionId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [sum, mon, cats, lrg, anom, txnsRes] = await Promise.all([
        fetchSummary(sessionId),
        fetchMonthlyTrends(sessionId),
        fetchCategoryBreakdown(sessionId, "expense"),
        fetchLargestTransactions(sessionId, 6, "expense"),
        fetchAnomalies(sessionId),
        fetchTransactions(sessionId, 100, 0),
      ]);

      setSummary(sum);
      setMonthlyTrends(mon);
      setCategories(cats);
      setLargestTxns(lrg);
      setAnomalies(anom);
      setTransactions(txnsRes.transactions);
      setTotalTxnCount(txnsRes.total_count);
    } catch (err: any) {
      setError(err.message || "Failed to load financial calculations.");
    } finally {
      setIsLoading(false);
    }
  };

  // 3. Handle File Upload
  const handleFileUpload = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await uploadFinancialFile(file);
      setUploadResult(res);
      await loadDashboardData(res.session_id);
    } catch (err: any) {
      setError(err.message || "File upload failed.");
      setIsLoading(false);
    }
  };

  // 4. Handle Sample Data Load (1-Click instant test)
  const handleLoadSample = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const sampleRes = await fetch("/sample_transactions.csv");
      if (!sampleRes.ok) throw new Error("Could not load sample CSV file.");
      const blob = await sampleRes.blob();
      const file = new File([blob], "sample_business_ledger.csv", {
        type: "text/csv",
      });
      await handleFileUpload(file);
    } catch (err: any) {
      setError(err.message || "Failed to load sample dataset.");
      setIsLoading(false);
    }
  };

  // 5. Purge and Reset Session
  const handleReset = async () => {
    if (uploadResult?.session_id) {
      try {
        await purgeSession(uploadResult.session_id);
      } catch {
        // silent cleanup
      }
    }
    setUploadResult(null);
    setSummary(null);
    setMonthlyTrends([]);
    setCategories([]);
    setLargestTxns([]);
    setAnomalies(null);
    setTransactions([]);
    setTotalTxnCount(0);
    setError(null);
  };

  const hasData = !!summary && !!uploadResult;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-emerald-500/20 selection:text-emerald-300">
      <Header
        health={health}
        onReset={handleReset}
        hasData={hasData}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Loading Skeleton Indicator */}
        {isLoading && !hasData && (
          <div className="py-20 flex flex-col items-center justify-center space-y-4">
            <div className="h-12 w-12 rounded-2xl bg-emerald-950/80 border border-emerald-800 flex items-center justify-center text-emerald-400">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
            <div className="text-center space-y-1">
              <p className="text-sm font-bold text-zinc-200">
                Processing Ledger &amp; Computing Metrics
              </p>
              <p className="text-xs text-zinc-400">
                Parsing rows, checking for anomalies, and building financial context...
              </p>
            </div>
          </div>
        )}

        {/* View A: Upload Area & Empty State */}
        {!hasData && !isLoading && (
          <div className="space-y-8 animate-in fade-in duration-300">
            <div className="text-center max-w-2xl mx-auto pt-6">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 mb-4">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Hacktoberfest 2026 Open Source Project</span>
              </div>
              <h2 className="text-3xl font-extrabold tracking-tight text-zinc-50 sm:text-4xl">
                Small Business Finance, <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                  Powered by Local AI
                </span>
              </h2>
              <p className="mt-3 text-sm text-zinc-400 leading-relaxed">
                Upload your bank statement or ledger spreadsheet. Get deterministic cash flow metrics,
                statistical outlier flags, and grounded plain-English AI explanations without sending private numbers to cloud APIs.
              </p>
            </div>

            <UploadZone
              onFileUpload={handleFileUpload}
              onLoadSample={handleLoadSample}
              isLoading={isLoading}
              error={error}
            />

            {/* Privacy Feature Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-4xl mx-auto pt-2">
              <div className="p-5 rounded-2xl border border-zinc-800 bg-zinc-900/60 shadow-xs">
                <div className="h-9 w-9 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 mb-3">
                  <Shield className="h-4.5 w-4.5" />
                </div>
                <h4 className="text-sm font-bold text-zinc-100">
                  100% On-Device Privacy
                </h4>
                <p className="text-xs text-zinc-400 mt-1.5 leading-relaxed">
                  Financial figures are analyzed entirely in your machine&apos;s memory with local open-weight models via Ollama. Zero external API calls.
                </p>
              </div>

              <div className="p-5 rounded-2xl border border-zinc-800 bg-zinc-900/60 shadow-xs">
                <div className="h-9 w-9 rounded-xl bg-blue-950/80 border border-blue-800/60 flex items-center justify-center text-blue-400 mb-3">
                  <CheckCircle2 className="h-4.5 w-4.5" />
                </div>
                <h4 className="text-sm font-bold text-zinc-100">
                  Zero Math Hallucinations
                </h4>
                <p className="text-xs text-zinc-400 mt-1.5 leading-relaxed">
                  Totals, growth percentages, and margins are calculated by deterministic Python algorithms, never guessed or approximated by an LLM.
                </p>
              </div>

              <div className="p-5 rounded-2xl border border-zinc-800 bg-zinc-900/60 shadow-xs">
                <div className="h-9 w-9 rounded-xl bg-purple-950/80 border border-purple-800/60 flex items-center justify-center text-purple-400 mb-3">
                  <FileSpreadsheet className="h-4.5 w-4.5" />
                </div>
                <h4 className="text-sm font-bold text-zinc-100">
                  Universal Format Support
                </h4>
                <p className="text-xs text-zinc-400 mt-1.5 leading-relaxed">
                  Ingests CSV and Excel formats from global banks, QuickBooks, Tally, or custom ledgers with dual Debit/Credit or signed Amount support.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* View B: Active Business Dashboard */}
        {hasData && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Active Dataset Status Banner */}
            <div className="p-4 rounded-2xl border border-zinc-800 bg-zinc-900/80 flex flex-wrap items-center justify-between gap-3 shadow-xs">
              <div className="flex items-center space-x-3.5">
                <div className="h-10 w-10 rounded-xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
                  <FileSpreadsheet className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-zinc-100">
                      {uploadResult.filename}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold bg-zinc-800 text-zinc-300 border border-zinc-700">
                      {uploadResult.file_type}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    {uploadResult.valid_transactions_count} verified transactions
                    {uploadResult.invalid_rows_count > 0 &&
                      ` (${uploadResult.invalid_rows_count} corrupt rows filtered)`}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="text-xs text-right hidden sm:block">
                  <span className="text-zinc-500">Statement Period: </span>
                  <span className="font-semibold text-zinc-200 font-mono">
                    {summary.start_date || "N/A"} → {summary.end_date || "N/A"}
                  </span>
                </div>
              </div>
            </div>

            {/* 1. Summary KPI Cards */}
            <KPICards summary={summary} />

            {/* 2. Visual Analytics Section: Cash Flow Chart + Category Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CashFlowChart data={monthlyTrends} />
              <CategoryChart categories={categories} />
            </div>

            {/* 3. AI Insights Section (Automated Executive Synthesis) */}
            <AIInsightsSection
              health={health}
              sessionId={uploadResult.session_id}
            />

            {/* 4. "Ask My Business" Interactive Q&A */}
            <AskMyBusinessSection sessionId={uploadResult.session_id} />

            {/* 5. Anomalies & Outliers + Largest Transactions */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <AnomaliesSection
                  report={anomalies}
                  sessionId={uploadResult.session_id}
                />
              </div>
              <div>
                <LargestExpensesSection transactions={largestTxns} />
              </div>
            </div>

            {/* 6. Normalized Transactions Table */}
            <TransactionsTable
              transactions={transactions}
              totalCount={totalTxnCount}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-zinc-800/80 py-6 text-center text-xs text-zinc-500">
        <p>
          LocalLedger AI — Privacy-First Business Financial Intelligence. Open Source for Hacktoberfest 2026.
        </p>
      </footer>
    </div>
  );
}
