"use client";

import React from "react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from "recharts";
import { CategoryBreakdown } from "@/types";
import { formatCurrency } from "@/lib/api";

interface CategoryChartProps {
  categories: CategoryBreakdown[];
}

const COLORS = [
  "#3b82f6", // Blue
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#8b5cf6", // Purple
  "#ec4899", // Pink
  "#06b6d4", // Cyan
  "#f97316", // Orange
  "#64748b", // Slate
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as CategoryBreakdown;
    return (
      <div className="bg-white dark:bg-zinc-900 p-3 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-md text-xs">
        <p className="font-semibold text-zinc-900 dark:text-zinc-100">{data.category}</p>
        <p className="text-zinc-700 dark:text-zinc-300 mt-1">
          Amount: {formatCurrency(data.amount)} ({data.percentage}%)
        </p>
        <p className="text-zinc-500 dark:text-zinc-400">
          Transactions: {data.transaction_count} (Avg: {formatCurrency(data.avg_per_transaction)})
        </p>
      </div>
    );
  }
  return null;
};

export const CategoryChart: React.FC<CategoryChartProps> = ({ categories }) => {
  if (!categories || categories.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-sm text-zinc-400">
        No category breakdown data available.
      </div>
    );
  }

  const topCategories = categories.slice(0, 6);

  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs flex flex-col justify-between">
      <div>
        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
          Expense Category Breakdown
        </h3>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Distribution of business expenditures by spending category
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center mt-3">
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={topCategories}
                dataKey="amount"
                nameKey="category"
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={3}
              >
                {topCategories.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    stroke="transparent"
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend list with exact amounts and percentages */}
        <div className="space-y-2 text-xs">
          {topCategories.map((cat, idx) => (
            <div key={cat.category} className="flex items-center justify-between">
              <div className="flex items-center space-x-2 truncate">
                <span
                  className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                />
                <span className="truncate text-zinc-700 dark:text-zinc-300 font-medium">
                  {cat.category}
                </span>
              </div>
              <div className="flex items-center space-x-2 flex-shrink-0">
                <span className="text-zinc-500 dark:text-zinc-400">
                  {cat.percentage}%
                </span>
                <span className="font-semibold text-zinc-900 dark:text-zinc-100">
                  {formatCurrency(cat.amount)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
