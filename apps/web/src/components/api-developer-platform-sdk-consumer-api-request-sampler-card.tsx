"use client";

import { useState } from "react";

interface RuleInfo { endpoint: string; sampleRate: number; conditions: string; }

export default function RequestSamplerCard() {
  const [rules] = useState<RuleInfo[]>([
    { endpoint: "/api/users", sampleRate: 0.1, conditions: "none" },
    { endpoint: "/api/search", sampleRate: 0.05, conditions: "latency > 100ms" },
    { endpoint: "/api/orders", sampleRate: 1.0, conditions: "status >= 400" },
  ]);
  const [stats] = useState({ evaluated: 125000, sampled: 8450, ratio: 6.76 });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Request Sampler</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Probabilistic request sampling for analytics</p>

      <div className="mt-4 space-y-2">
        {rules.map((r) => (
          <div key={r.endpoint} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{r.endpoint}</span>
            <div className="text-xs text-zinc-500">
              {(r.sampleRate * 100).toFixed(0)}% · {r.conditions}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {stats.sampled.toLocaleString()} sampled / {stats.evaluated.toLocaleString()} evaluated ({stats.ratio}%)
      </div>
    </div>
  );
}
