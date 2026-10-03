"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileSpreadsheet, AlertCircle, Sparkles, Loader2, ArrowRight } from "lucide-react";

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
    <div className="w-full max-w-4xl mx-auto my-6 space-y-4">
      {error && (
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-800/80 text-rose-300 text-xs flex items-start space-x-3 shadow-sm animate-in fade-in duration-200">
          <AlertCircle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-rose-200">File Processing Notice</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 bg-zinc-900/60 hover:bg-zinc-900/90 shadow-sm ${
          isDragOver
            ? "border-emerald-500 bg-emerald-950/20 scale-[1.01]"
            : "border-zinc-800 hover:border-zinc-700"
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
          <div className="h-16 w-16 rounded-2xl bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400 shadow-inner">
            {isLoading ? (
              <Loader2 className="h-8 w-8 animate-spin" />
            ) : (
              <UploadCloud className="h-8 w-8" />
            )}
          </div>

          <div className="space-y-1.5 max-w-md">
            <h3 className="text-lg font-bold text-zinc-100">
              {isLoading
                ? "Parsing & Normalizing Financial Ledger..."
                : "Drop your bank statement or expense ledger here"}
            </h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Upload bank exports (.CSV, .XLSX, .XLS) up to 10MB. Files are processed entirely in local memory with zero cloud exfiltration.
            </p>
          </div>

          {/* Formats badges */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700">
              <FileSpreadsheet className="h-3.5 w-3.5 mr-1 text-emerald-400" />
              CSV (.csv)
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700">
              <FileSpreadsheet className="h-3.5 w-3.5 mr-1 text-emerald-400" />
              Excel (.xlsx / .xls)
            </span>
            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700">
              Auto-Maps Debit &amp; Credit
            </span>
          </div>

          {/* 1-Click Sample Dataset Button */}
          <div className="pt-3 border-t border-zinc-800/80 w-full max-w-sm mx-auto">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onLoadSample();
              }}
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 transition active:scale-98 cursor-pointer disabled:opacity-50"
            >
              <Sparkles className="h-4 w-4 text-emerald-400" />
              <span>Load Realistic Demo Dataset (1-Click)</span>
              <ArrowRight className="h-3.5 w-3.5 text-emerald-400" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
