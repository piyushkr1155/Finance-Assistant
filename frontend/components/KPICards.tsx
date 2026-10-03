"use client";

import React from "react";
import { TrendingUp, TrendingDown, DollarSign, Activity } from "lucide-react";
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
      <div className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            Total Income
          </span>
          <div className="h-8 w-8 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            <TrendingUp className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
            {formatCurrency(summary.total_income)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
            <span>{summary.income_transaction_count} income receipts</span>
            {summary.top_income_category && (
              <span className="truncate max-w-[120px] font-medium text-zinc-700 dark:text-zinc-300">
                Top: {summary.top_income_category}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 2. Total Expenses */}
      <div className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            Total Expenses
          </span>
          <div className="h-8 w-8 rounded-lg bg-rose-50 dark:bg-rose-950/60 flex items-center justify-center text-rose-600 dark:text-rose-400">
            <TrendingDown className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
            {formatCurrency(summary.total_expenses)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
            <span>{summary.expense_transaction_count} disbursements</span>
            {summary.top_expense_category && (
              <span className="truncate max-w-[120px] font-medium text-zinc-700 dark:text-zinc-300">
                Top: {summary.top_expense_category}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* 3. Net Cash Flow */}
      <div className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            Net Cash Flow
          </span>
          <div
            className={`h-8 w-8 rounded-lg flex items-center justify-center ${
              isNetPositive
                ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400"
                : "bg-rose-50 text-rose-600 dark:bg-rose-950/60 dark:text-rose-400"
            }`}
          >
            <DollarSign className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2
            className={`text-2xl font-bold tracking-tight ${
              isNetPositive
                ? "text-emerald-600 dark:text-emerald-400"
                : "text-rose-600 dark:text-rose-400"
            }`}
          >
            {formatCurrency(summary.net_cash_flow)}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs">
            <span
              className={`font-semibold ${
                isNetPositive
                  ? "text-emerald-600 dark:text-emerald-400"
                  : "text-rose-600 dark:text-rose-400"
              }`}
            >
              {isNetPositive ? "Surplus" : "Deficit"}
            </span>
            <span className="text-zinc-500 dark:text-zinc-400">
              Margin: {formatPercentage(summary.savings_rate_pct)}
            </span>
          </div>
        </div>
      </div>

      {/* 4. Transactions & Scope */}
      <div className="p-5 bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            Transactions
          </span>
          <div className="h-8 w-8 rounded-lg bg-blue-50 dark:bg-blue-950/60 flex items-center justify-center text-blue-600 dark:text-blue-400">
            <Activity className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3">
          <h2 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
            {summary.transaction_count}
          </h2>
          <div className="mt-2 flex items-center justify-between text-xs text-zinc-500 dark:text-zinc-400">
            <span>Avg: {formatCurrency(summary.avg_transaction_amount)}</span>
            {summary.start_date && summary.end_date && (
              <span className="text-[11px] truncate text-zinc-400">
                {summary.start_date.slice(5)} to {summary.end_date.slice(5)}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
