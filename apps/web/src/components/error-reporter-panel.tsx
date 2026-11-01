"use client";

import { useState } from "react";

interface ErrorGroup {
  fingerprint: string;
  message: string;
  errorType: string;
  count: number;
  firstSeen: string;
  lastSeen: string;
  resolved: boolean;
}

interface ErrorStats {
  totalErrors: number;
  uniqueErrors: number;
  unresolved: number;
  ratePerMinute: number;
}

export function ErrorReporterPanel({
  groups,
  stats,
  onResolve,
}: {
  groups: ErrorGroup[];
  stats: ErrorStats;
  onResolve?: (fingerprint: string) => void;
}) {
  const [filter, setFilter] = useState<"all" | "unresolved" | "resolved">("unresolved");

  const filtered = filter === "all" ? groups
    : filter === "unresolved" ? groups.filter((g) => !g.resolved)
    : groups.filter((g) => g.resolved);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🐞 Error Reporter</h2>
        <span className={`text-sm font-bold ${stats.unresolved > 0 ? "text-red-600" : "text-green-600"}`}>
          {stats.unresolved} unresolved
        </span>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Total</span>
          <span className="font-bold text-lg">{stats.totalErrors}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Unique</span>
          <span className="font-bold text-lg">{stats.uniqueErrors}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Unresolved</span>
          <span className="font-bold text-lg text-red-600">{stats.unresolved}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Rate</span>
          <span className="font-bold text-lg">{stats.ratePerMinute}/min</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["unresolved", "all", "resolved"] as const).map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`text-xs px-3 py-1 rounded-lg ${filter === f ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((g) => (
          <div key={g.fingerprint} className={`rounded-lg border dark:border-gray-700 p-3 ${g.resolved ? "opacity-50" : ""}`}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs bg-red-100 dark:bg-red-900/30 text-red-600 px-1.5 py-0.5 rounded">{g.errorType}</span>
                <span className="text-sm font-medium">{g.message}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-red-500">×{g.count}</span>
                {!g.resolved && (
                  <button onClick={() => onResolve?.(g.fingerprint)}
                    className="text-xs bg-green-600 text-white px-2 py-0.5 rounded">Resolve</button>
                )}
              </div>
            </div>
            <div className="text-xs text-gray-400">
              First: {g.firstSeen} · Last: {g.lastSeen}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
