"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { MonthlyMetric } from "@/types";
import { formatCurrency } from "@/lib/api";

interface CashFlowChartProps {
  data: MonthlyMetric[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const income = payload.find((p: any) => p.dataKey === "income")?.value || 0;
    const expenses = payload.find((p: any) => p.dataKey === "expenses")?.value || 0;
    const net = income - expenses;

    return (
      <div className="bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-md text-xs">
        <p className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">{label}</p>
        <div className="space-y-1">
          <p className="text-emerald-600 dark:text-emerald-400">
            Income: {formatCurrency(income)}
          </p>
          <p className="text-rose-600 dark:text-rose-400">
            Expenses: {formatCurrency(expenses)}
          </p>
          <p
            className={`font-semibold border-t border-zinc-100 dark:border-zinc-800 pt-1 ${
              net >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
            }`}
          >
            Net Cash Flow: {formatCurrency(net)}
          </p>
        </div>
      </div>
    );
  }
  return null;
};

export const CashFlowChart: React.FC<CashFlowChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-zinc-400">
        No monthly trend data available.
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
          Monthly Income vs Expenses
        </h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Deterministic month-by-month cash flow comparison
        </p>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.15} />
            <XAxis
              dataKey="month"
              tickLine={false}
              tick={{ fontSize: 11, fill: "#71717a" }}
              axisLine={{ stroke: "#e4e4e7" }}
            />
            <YAxis
              tickLine={false}
              tick={{ fontSize: 11, fill: "#71717a" }}
              axisLine={false}
              tickFormatter={(v) => `₹${v >= 1000 ? `${Math.round(v / 1000)}k` : v}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }}
              formatter={(value) => (value === "income" ? "Income" : "Expenses")}
            />
            <Bar dataKey="income" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={36} />
            <Bar dataKey="expenses" fill="#f43f5e" radius={[4, 4, 0, 0]} maxBarSize={36} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
