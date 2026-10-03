"use client";

import React from "react";
import { ArrowUpRight } from "lucide-react";
import { LargestTransaction } from "@/types";
import { formatCurrency } from "@/lib/api";

interface LargestExpensesProps {
  transactions: LargestTransaction[];
}

export const LargestExpensesSection: React.FC<LargestExpensesProps> = ({
  transactions,
}) => {
  if (!transactions || transactions.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Largest Transactions
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Highest value individual inflows and outflows
          </p>
        </div>
        <ArrowUpRight className="h-5 w-5 text-zinc-400" />
      </div>

      <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
        {transactions.map((t) => (
          <div
            key={t.id}
            className="py-2.5 flex items-center justify-between text-xs"
          >
            <div className="truncate mr-3">
              <p className="font-semibold text-zinc-800 dark:text-zinc-200 truncate">
                {t.description}
              </p>
              <div className="flex items-center space-x-2 text-zinc-400 mt-0.5">
                <span>{t.date}</span>
                <span>•</span>
                <span className="truncate">{t.category}</span>
              </div>
            </div>
            <div className="text-right flex-shrink-0">
              <span
                className={`font-bold ${
                  t.type === "income"
                    ? "text-emerald-600 dark:text-emerald-400"
                    : "text-zinc-900 dark:text-zinc-100"
                }`}
              >
                {t.type === "income" ? "+" : "-"}
                {formatCurrency(t.amount)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
