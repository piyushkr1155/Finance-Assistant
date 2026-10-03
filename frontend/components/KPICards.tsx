"use client";

import React from "react";
import { TrendingUp, TrendingDown, DollarSign, Activity, HelpCircle } from "lucide-react";
import { SummaryKPIs } from "@/types";
import { formatCurrency, formatPercentage } from "@/lib/api";

interface KPICardsProps {
  summary: SummaryKPIs;
}

export const KPICards: React.FC<KPICardsProps> = ({ summary }) => {
  const isNetPositive = summary.net_cash_flow >= 0;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 my-6">
      {/* 1. Total Income */}
      <div className="p-5 bg-zinc-900/90 rounded-2xl border border-zinc-800 shadow-sm hover:border-zinc-700 transition-all duration-200 group">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1.5">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
              Total Revenue
            </span>
          </div>
          <div className="h-8 w-8 rounded-lg bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
            <TrendingUp className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">
            {formatCurrency(summary.total_income)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-400">
            <span>{summary.income_transaction_count} income receipts</span>
            {summary.top_income_category && (
              <span className="truncate max-w-[130px] font-medium text-emerald-400" title={`Top: ${summary.top_income_category}`}>
                {summary.top_income_category}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 2. Total Expenses */}
      <div className="p-5 bg-zinc-900/90 rounded-2xl border border-zinc-800 shadow-sm hover:border-zinc-700 transition-all duration-200 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
            Total Expenditures
          </span>
          <div className="h-8 w-8 rounded-lg bg-rose-950/80 border border-rose-800/60 flex items-center justify-center text-rose-400 group-hover:scale-110 transition-transform">
            <TrendingDown className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">
            {formatCurrency(summary.total_expenses)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-400">
            <span>{summary.expense_transaction_count} disbursements</span>
            {summary.top_expense_category && (
              <span className="truncate max-w-[130px] font-medium text-rose-400" title={`Top: ${summary.top_expense_category}`}>
                {summary.top_expense_category}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 3. Net Cash Flow */}
      <div className="p-5 bg-zinc-900/90 rounded-2xl border border-zinc-800 shadow-sm hover:border-zinc-700 transition-all duration-200 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
            Net Cash Flow
          </span>
          <div
            className={`h-8 w-8 rounded-lg border flex items-center justify-center group-hover:scale-110 transition-transform ${
              isNetPositive
                ? "bg-emerald-950/80 border-emerald-800/60 text-emerald-400"
                : "bg-rose-950/80 border-rose-800/60 text-rose-400"
            }`}
          >
            <DollarSign className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2
            className={`text-2xl font-bold tracking-tight ${
              isNetPositive ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {formatCurrency(summary.net_cash_flow)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs">
            <span
              className={`font-semibold ${
                isNetPositive ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {isNetPositive ? "Operating Surplus" : "Operating Deficit"}
            </span>
            <span className="text-zinc-500">Revenue - Expenses</span>
          </div>
        </div>
      </div>

      {/* 4. Savings Rate / Net Margin */}
      <div className="p-5 bg-zinc-900/90 rounded-2xl border border-zinc-800 shadow-sm hover:border-zinc-700 transition-all duration-200 group">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
            Net Margin / Retention
          </span>
          <div className="h-8 w-8 rounded-lg bg-blue-950/80 border border-blue-800/60 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
            <Activity className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-100">
            {formatPercentage(summary.savings_rate_pct)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-400">
            <span>
              {summary.savings_rate_pct >= 20 ? (
                <span className="text-emerald-400 font-medium">Healthy Buffer</span>
              ) : summary.savings_rate_pct >= 0 ? (
                <span className="text-amber-400 font-medium">Lean Margin</span>
              ) : (
                <span className="text-rose-400 font-medium">Negative Margin</span>
              )}
            </span>
            <span className="text-zinc-500">{summary.transaction_count} Total Records</span>
          </div>
        </div>
      </div>
    </div>
  );
};
