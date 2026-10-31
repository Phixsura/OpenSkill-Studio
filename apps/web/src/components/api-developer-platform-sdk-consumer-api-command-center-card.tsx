"use client";

import { useState } from "react";

export default function CommandCenterCard() {
  const [overview] = useState({
    platformStatus: "all_operational",
    services: { total: 12, operational: 11, degraded: 1, outage: 0 },
    metrics: { consumers: 250, endpoints: 85, requests24h: 1250000, avgLatency: 42, errorRate: 0.3 },
    healthScore: 97.5,
    healthGrade: "B",
  });

  const statusColor = overview.platformStatus === "all_operational"
    ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
    : overview.platformStatus === "partial_outage"
    ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
    : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300";

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">🎯 Command Center</h3>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusColor}`}>
          {overview.platformStatus.replace(/_/g, " ")}
        </span>
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Unified platform overview — pair #1100
      </p>

      <div className="mt-4 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{overview.metrics.consumers}</div>
          <div className="text-xs text-zinc-500">Consumers</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{overview.metrics.endpoints}</div>
          <div className="text-xs text-zinc-500">Endpoints</div>
        </div>
        <div className="rounded-lg bg-zinc-50 p-2 dark:bg-zinc-800">
          <div className="text-lg font-bold text-zinc-900 dark:text-zinc-100">{overview.healthGrade}</div>
          <div className="text-xs text-zinc-500">Health</div>
        </div>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
        <div className="text-green-600 dark:text-green-400">{overview.services.operational} operational</div>
        <div className="text-amber-600 dark:text-amber-400">{overview.services.degraded} degraded</div>
        <div className="text-zinc-500">{overview.metrics.avgLatency}ms avg</div>
      </div>

      <div className="mt-3 flex justify-between text-xs text-zinc-400 dark:text-zinc-500">
        <span>{(overview.metrics.requests24h / 1000000).toFixed(1)}M requests/24h</span>
        <span>{overview.metrics.errorRate}% error rate</span>
      </div>
    </div>
  );
}
