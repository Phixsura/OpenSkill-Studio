"use client";

import { useState } from "react";

export default function ReqLoggerCard() {
  const [summary] = useState({
    total: 45200, byLevel: { info: 42500, warn: 2100, error: 600 },
    avgLatency: 68, errorRate: 1.33,
  });

  const LEVEL_COLOR: Record<string, string> = {
    info: "text-blue-600 dark:text-blue-400",
    warn: "text-amber-600 dark:text-amber-400",
    error: "text-red-600 dark:text-red-400",
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Request Logger</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Structured request logging with search</p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        {Object.entries(summary.byLevel).map(([level, count]) => (
          <div key={level} className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
            <div className={`text-lg font-bold ${LEVEL_COLOR[level] ?? ""}`}>{count.toLocaleString()}</div>
            <div className="text-xs text-zinc-500">{level}</div>
          </div>
        ))}
      </div>

      <div className="mt-3 flex justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{summary.total.toLocaleString()} total</span>
        <span>{summary.avgLatency}ms avg</span>
        <span>{summary.errorRate}% errors</span>
      </div>
    </div>
  );
}
