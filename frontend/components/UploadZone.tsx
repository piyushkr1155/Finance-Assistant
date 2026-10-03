"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileSpreadsheet, AlertCircle, Sparkles, Loader2 } from "lucide-react";

interface UploadZoneProps {
  onFileUpload: (file: File) => void;
  onLoadSample: () => void;
  isLoading: boolean;
  error: string | null;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileUpload,
  onLoadSample,
  isLoading,
  error,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto my-8">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 ${
          isDragOver
            ? "border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20"
            : "border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900/50 hover:border-zinc-400 dark:hover:border-zinc-600"
        } ${isLoading ? "pointer-events-none opacity-80" : ""}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={handleFileChange}
          disabled={isLoading}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="h-16 w-16 rounded-full bg-emerald-100 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
            {isLoading ? (
              <Loader2 className="h-8 w-8 animate-spin" />
            ) : (
              <UploadCloud className="h-8 w-8" />
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
              {isLoading
                ? "Parsing & Normalizing Financial Ledger..."
                : "Drop your CSV or Excel file here, or browse"}
            </h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Supports CSV, XLSX, and XLS exports from bank statements, Tally, or QuickBooks (up to 10MB)
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
            <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
              <FileSpreadsheet className="h-3.5 w-3.5 mr-1 text-emerald-600" />
              .CSV
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
              <FileSpreadsheet className="h-3.5 w-3.5 mr-1 text-emerald-600" />
              .XLSX / .XLS
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300">
              Flexible Column Auto-Mapping
            </span>
          </div>

          <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800 w-full max-w-sm flex items-center justify-center">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onLoadSample();
              }}
              disabled={isLoading}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950 hover:bg-emerald-100 dark:hover:bg-emerald-900 border border-emerald-200 dark:border-emerald-800 transition shadow-sm"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Or click here to load Sample Business Dataset</span>
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 rounded-lg bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 flex items-start space-x-3 text-rose-800 dark:text-rose-300">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
          <div className="text-sm">
            <p className="font-semibold">Upload Error</p>
            <p>{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};
