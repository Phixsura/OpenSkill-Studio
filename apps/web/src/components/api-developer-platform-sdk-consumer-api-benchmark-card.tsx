"use client";

import { useState } from "react";

interface RunInfo { runId: string; endpoint: string; rps: number; p95Ms: number; errorRate: number; }

export default function BenchmarkCard() {
  const [runs] = useState<RunInfo[]>([
    { runId: "run-1", endpoint: "/api/users", rps: 1250, p95Ms: 45, errorRate: 0.1 },
    { runId: "run-2", endpoint: "/api/search", rps: 340, p95Ms: 320, errorRate: 1.5 },
    { runId: "run-3", endpoint: "/api/orders", rps: 890, p95Ms: 85, errorRate: 0.3 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Endpoint Benchmark</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Performance benchmarking with comparison</p>

      <div className="mt-4 space-y-2">
        {runs.map((r) => (
          <div key={r.runId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{r.endpoint}</span>
            <div className="flex items-center gap-3 text-xs text-zinc-500">
              <span>{r.rps.toLocaleString()} rps</span>
              <span>P95: {r.p95Ms}ms</span>
              <span>{r.errorRate}% err</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{runs.length} benchmark runs</div>
    </div>
  );
}
