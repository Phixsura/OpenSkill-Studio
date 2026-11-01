"use client";

import { useState } from "react";

interface LogSummary {
  total: number;
  success: number;
  clientErrors: number;
  serverErrors: number;
  successRate: number;
  avgLatencyMs: number;
}

export default function AccessLogCard() {
  const [summary] = useState<LogSummary>({
    total: 15420,
    success: 14800,
    clientErrors: 520,
    serverErrors: 100,
    successRate: 96.0,
    avgLatencyMs: 85,
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Access Log
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Structured access logging with search
      </p>

      <div className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div>
          <div className="text-xl font-bold text-green-600 dark:text-green-400">{summary.successRate}%</div>
          <div className="text-xs text-zinc-500">Success Rate</div>
        </div>
        <div>
          <div className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{summary.avgLatencyMs}ms</div>
          <div className="text-xs text-zinc-500">Avg Latency</div>
        </div>
        <div>
          <div className="text-xl font-bold text-zinc-900 dark:text-zinc-100">{summary.total.toLocaleString()}</div>
          <div className="text-xs text-zinc-500">Total</div>
        </div>
      </div>

      <div className="mt-3 flex gap-3 text-xs">
        <span className="text-green-600 dark:text-green-400">{summary.success.toLocaleString()} success</span>
        <span className="text-amber-600 dark:text-amber-400">{summary.clientErrors} client err</span>
        <span className="text-red-600 dark:text-red-400">{summary.serverErrors} server err</span>
      </div>
    </div>
  );
}
