"use client";

import React, { useState } from "react";
import { Search, Filter } from "lucide-react";
import { Transaction } from "@/types";
import { formatCurrency } from "@/lib/api";

interface TransactionsTableProps {
  transactions: Transaction[];
  totalCount: number;
}

export const TransactionsTable: React.FC<TransactionsTableProps> = ({
  transactions,
  totalCount,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<"all" | "income" | "expense">("all");

  const filtered = transactions.filter((t) => {
    const matchesSearch =
      t.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType =
      filterType === "all" || t.type.toLowerCase() === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-xs overflow-hidden my-6">
      {/* Header & Controls */}
      <div className="p-5 border-b border-zinc-200 dark:border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
            Normalized Transactions
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Showing {filtered.length} of {totalCount} verified records
          </p>
        </div>

        {/* Filter & Search */}
        <div className="flex items-center space-x-2">
          {/* Type Filter Buttons */}
          <div className="inline-flex rounded-lg border border-zinc-200 dark:border-zinc-700 p-0.5 bg-zinc-50 dark:bg-zinc-800 text-xs font-medium">
            <button
              onClick={() => setFilterType("all")}
              className={`px-2.5 py-1 rounded-md transition ${
                filterType === "all"
                  ? "bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 shadow-xs"
                  : "text-zinc-500 dark:text-zinc-400 hover:text-zinc-900"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType("income")}
              className={`px-2.5 py-1 rounded-md transition ${
                filterType === "income"
                  ? "bg-white dark:bg-zinc-900 text-emerald-600 dark:text-emerald-400 shadow-xs"
                  : "text-zinc-500 dark:text-zinc-400 hover:text-emerald-600"
              }`}
            >
              Income
            </button>
            <button
              onClick={() => setFilterType("expense")}
              className={`px-2.5 py-1 rounded-md transition ${
                filterType === "expense"
                  ? "bg-white dark:bg-zinc-900 text-rose-600 dark:text-rose-400 shadow-xs"
                  : "text-zinc-500 dark:text-zinc-400 hover:text-rose-600"
              }`}
            >
              Expenses
            </button>
          </div>

          {/* Search input */}
          <div className="relative">
            <Search className="h-4 w-4 absolute left-2.5 top-2.5 text-zinc-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:outline-hidden focus:ring-1 focus:ring-emerald-500 w-36 sm:w-48"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-zinc-50 dark:bg-zinc-800/50 text-zinc-500 dark:text-zinc-400 border-b border-zinc-200 dark:border-zinc-800 uppercase tracking-wider text-[11px]">
            <tr>
              <th className="py-3 px-4">Date</th>
              <th className="py-3 px-4">Description</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4 text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800 text-zinc-700 dark:text-zinc-300">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-zinc-400">
                  No matching transactions found.
                </td>
              </tr>
            ) : (
              filtered.map((t) => (
                <tr
                  key={t.id}
                  className="hover:bg-zinc-50/60 dark:hover:bg-zinc-800/40 transition"
                >
                  <td className="py-2.5 px-4 font-mono text-zinc-500 dark:text-zinc-400">
                    {t.date}
                  </td>
                  <td className="py-2.5 px-4 font-medium text-zinc-900 dark:text-zinc-100">
                    {t.description}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className="inline-block px-2 py-0.5 rounded text-[11px] bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300">
                      {t.category}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold capitalize ${
                        t.type === "income"
                          ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300"
                          : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                      }`}
                    >
                      {t.type}
                    </span>
                  </td>
                  <td
                    className={`py-2.5 px-4 text-right font-bold ${
                      t.type === "income"
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-zinc-900 dark:text-zinc-100"
                    }`}
                  >
                    {t.type === "income" ? "+" : "-"}
                    {formatCurrency(t.amount)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
