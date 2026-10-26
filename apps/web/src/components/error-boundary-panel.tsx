"use client";

import { useState } from "react";

interface CaughtError {
  id: string;
  category: string;
  message: string;
  actionTaken: "retry" | "skip" | "halt" | "fallback";
  resolved: boolean;
  timestamp: string;
}

interface ErrorSummary {
  total: number;
  byCategory: Record<string, number>;
  circuitOpen: boolean;
  errorRate: number;
}

const categoryIcons: Record<string, string> = {
  runtime: "💥", timeout: "⏰", memory: "🧠", network: "🌐",
  permission: "🔒", validation: "📋", dependency: "📦", unknown: "❓",
};

const actionColors: Record<string, string> = {
  retry: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  skip: "bg-gray-100 text-gray-600 dark:bg-gray-800",
  halt: "bg-red-100 text-red-600 dark:bg-red-900/30",
  fallback: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
};

export function ErrorBoundaryPanel({
  errors,
  summary,
  onResolve,
  onResetCircuit,
}: {
  errors: CaughtError[];
  summary: ErrorSummary;
  onResolve?: (id: string) => void;
  onResetCircuit?: () => void;
}) {
  const [catFilter, setCatFilter] = useState<string>("all");
  const filtered = catFilter === "all" ? errors : errors.filter((e) => e.category === catFilter);
  const categories = Object.keys(summary.byCategory);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🛡️ Error Boundary</h2>
        <div className="flex items-center gap-2">
          {summary.circuitOpen && (
            <div className="flex items-center gap-1">
              <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full animate-pulse">Circuit OPEN</span>
              <button onClick={onResetCircuit}
                className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Reset</button>
            </div>
          )}
          <span className="text-sm text-gray-500">{summary.total} errors</span>
        </div>
      </div>

      {categories.length > 0 && (
        <div className="flex gap-1 flex-wrap">
          <button onClick={() => setCatFilter("all")}
            className={`text-xs px-2.5 py-1 rounded-full ${catFilter === "all" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            All ({summary.total})
          </button>
          {categories.map((cat) => (
            <button key={cat} onClick={() => setCatFilter(cat)}
              className={`text-xs px-2.5 py-1 rounded-full ${catFilter === cat ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
              {categoryIcons[cat] || "❓"} {cat} ({summary.byCategory[cat]})
            </button>
          ))}
        </div>
      )}

      <div className="space-y-1">
        {filtered.map((err) => (
          <div key={err.id} className={`rounded-lg border dark:border-gray-700 p-3 ${err.resolved ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span>{categoryIcons[err.category] || "❓"}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${actionColors[err.actionTaken]}`}>{err.actionTaken}</span>
                <span className="text-xs text-gray-400">{err.timestamp}</span>
              </div>
              {!err.resolved && (
                <button onClick={() => onResolve?.(err.id)}
                  className="text-xs bg-green-600 text-white px-2 py-1 rounded">Resolve</button>
              )}
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">{err.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
