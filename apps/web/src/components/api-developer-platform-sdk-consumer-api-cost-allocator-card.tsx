"use client";

import { useState } from "react";

interface CostEntry {
  endpointId: string;
  computeCents: number;
  bandwidthCents: number;
  totalDollars: number;
}

export default function CostAllocatorCard() {
  const [costs] = useState<CostEntry[]>([
    { endpointId: "ep-users", computeCents: 4500, bandwidthCents: 1200, totalDollars: 57.0 },
    { endpointId: "ep-search", computeCents: 8900, bandwidthCents: 3400, totalDollars: 123.0 },
    { endpointId: "ep-uploads", computeCents: 1200, bandwidthCents: 8500, totalDollars: 97.0 },
  ]);

  const totalDollars = costs.reduce((s, c) => s + c.totalDollars, 0);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Cost Allocator
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Per-endpoint cost tracking with attribution
      </p>

      <div className="mt-4 space-y-2">
        {costs.map((c) => (
          <div key={c.endpointId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{c.endpointId}</span>
            <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              ${c.totalDollars.toFixed(2)}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{costs.length} endpoints</span>
        <span className="font-semibold text-zinc-700 dark:text-zinc-300">Total: ${totalDollars.toFixed(2)}</span>
      </div>
    </div>
  );
}
