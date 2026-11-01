"use client";

import { useState } from "react";

interface PercentileData {
  endpointId: string;
  p50: number;
  p95: number;
  p99: number;
}

export default function LatencyHeatmapCard() {
  const [data] = useState<PercentileData[]>([
    { endpointId: "ep-auth", p50: 12, p95: 45, p99: 120 },
    { endpointId: "ep-search", p50: 85, p95: 320, p99: 890 },
    { endpointId: "ep-upload", p50: 150, p95: 680, p99: 2100 },
  ]);

  const getColor = (ms: number) => {
    if (ms < 100) return "bg-green-200 dark:bg-green-800";
    if (ms < 500) return "bg-yellow-200 dark:bg-yellow-800";
    return "bg-red-200 dark:bg-red-800";
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Latency Heatmap
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Time-bucket latency distribution
      </p>

      <div className="mt-4 space-y-2">
        {data.map((d) => (
          <div key={d.endpointId} className="rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="text-sm font-mono text-zinc-800 dark:text-zinc-200 mb-1">{d.endpointId}</div>
            <div className="flex gap-1">
              <div className={`flex-1 rounded px-2 py-1 text-center text-xs ${getColor(d.p50)}`}>P50: {d.p50}ms</div>
              <div className={`flex-1 rounded px-2 py-1 text-center text-xs ${getColor(d.p95)}`}>P95: {d.p95}ms</div>
              <div className={`flex-1 rounded px-2 py-1 text-center text-xs ${getColor(d.p99)}`}>P99: {d.p99}ms</div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {data.length} endpoints tracked
      </div>
    </div>
  );
}
