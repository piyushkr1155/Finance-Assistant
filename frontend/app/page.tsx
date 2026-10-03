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
} from "@/lib/api";

import { FileSpreadsheet, CheckCircle2, Shield, Info, Loader2 } from "lucide-react";

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
        // Backend not yet reachable or starting up
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
        fetchLargestTransactions(sessionId, 6),
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

  // 5. Reset to upload state
  const handleReset = () => {
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
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 flex flex-col font-sans">
      <Header
        health={health}
        onReset={handleReset}
        hasData={hasData}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Loading Spinner Indicator */}
        {isLoading && !hasData && (
          <div className="py-20 flex flex-col items-center justify-center space-y-3">
            <Loader2 className="h-10 w-10 text-emerald-600 animate-spin" />
            <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
              Processing financial ledger and verifying numbers...
            </p>
          </div>
        )}

        {/* View A: Upload Area & Empty State */}
        {!hasData && !isLoading && (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto pt-6">
              <h2 className="text-3xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-4xl">
                Small Business Finance, <br />
                <span className="text-emerald-600 dark:text-emerald-400">
                  Powered by Local AI
                </span>
              </h2>
              <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
                Upload your business bank statement or expense spreadsheet.
                Get instant cash flow trends, deterministic category totals, and
                plain-English AI insights without uploading your private numbers to cloud APIs.
              </p>
            </div>

            <UploadZone
              onFileUpload={handleFileUpload}
              onLoadSample={handleLoadSample}
              isLoading={isLoading}
              error={error}
            />

            {/* Privacy Feature Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto pt-4">
              <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
                <div className="h-8 w-8 rounded-lg bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 mb-2">
                  <Shield className="h-4 w-4" />
                </div>
                <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                  100% On-Device Privacy
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                  Financial figures are processed in memory and analyzed with your local Ollama LLM. Zero external cloud tracking.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
                <div className="h-8 w-8 rounded-lg bg-blue-100 dark:bg-blue-950 flex items-center justify-center text-blue-600 mb-2">
                  <CheckCircle2 className="h-4 w-4" />
                </div>
                <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                  Zero Hallucinations
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                  Totals, growth percentages, and balances are calculated by deterministic Python algorithms, never guessed by AI.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
                <div className="h-8 w-8 rounded-lg bg-purple-100 dark:bg-purple-950 flex items-center justify-center text-purple-600 mb-2">
                  <FileSpreadsheet className="h-4 w-4" />
                </div>
                <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                  Universal Format Support
                </h4>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                  Works with CSV or Excel exports from Indian, US, and EU banks, QuickBooks, Tally, or custom spreadsheets.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* View B: Active Business Dashboard */}
        {hasData && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Active Dataset Status Banner */}
            <div className="p-3.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 flex flex-wrap items-center justify-between gap-3 shadow-xs">
              <div className="flex items-center space-x-3">
                <div className="h-9 w-9 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                  <FileSpreadsheet className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                      {uploadResult.filename}
                    </span>
                    <span className="text-[11px] px-2 py-0.5 rounded font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300">
                      {uploadResult.file_type}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400">
                    {uploadResult.valid_transactions_count} verified transactions
                    {uploadResult.invalid_rows_count > 0 &&
                      ` (${uploadResult.invalid_rows_count} rejected corrupt rows)`}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="text-xs text-right hidden sm:block">
                  <span className="text-zinc-400">Date Range: </span>
                  <span className="font-medium text-zinc-700 dark:text-zinc-300">
                    {summary.start_date || "N/A"} to {summary.end_date || "N/A"}
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
                <AnomaliesSection report={anomalies} />
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
      <footer className="mt-auto border-t border-zinc-200 dark:border-zinc-800 py-6 text-center text-xs text-zinc-500 dark:text-zinc-400">
        <p>
          LocalLedger AI — Privacy-First Business Financial Intelligence. Open Source for Hacktoberfest 2026.
        </p>
      </footer>
    </div>
  );
}
