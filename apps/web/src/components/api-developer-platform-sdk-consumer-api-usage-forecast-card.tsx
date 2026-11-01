"use client";

import { useState } from "react";

interface ForecastInfo {
  metricId: string;
  direction: string;
  growthRate: number;
  latest: number;
  forecasted: number[];
}

export default function UsageForecastCard() {
  const [forecasts] = useState<ForecastInfo[]>([
    { metricId: "API Calls", direction: "increasing", growthRate: 0.15, latest: 45000, forecasted: [51750, 59512, 68439] },
    { metricId: "Data Transfer", direction: "stable", growthRate: 0.02, latest: 12800, forecasted: [13056, 13317, 13583] },
  ]);

  const DIR_ICON: Record<string, string> = { increasing: "↑", decreasing: "↓", stable: "→" };
  const DIR_COLOR: Record<string, string> = {
    increasing: "text-green-600 dark:text-green-400",
    decreasing: "text-red-600 dark:text-red-400",
    stable: "text-blue-600 dark:text-blue-400",
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Usage Forecast
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Time-series forecasting with trend projection
      </p>

      <div className="mt-4 space-y-3">
        {forecasts.map((f) => (
          <div key={f.metricId} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="font-medium text-zinc-900 dark:text-zinc-100">{f.metricId}</span>
              <span className={`text-sm font-semibold ${DIR_COLOR[f.direction]}`}>
                {DIR_ICON[f.direction]} {(f.growthRate * 100).toFixed(0)}%
              </span>
            </div>
            <div className="mt-1 text-xs text-zinc-500">
              Current: {f.latest.toLocaleString()} → Next 3: {f.forecasted.map((v) => v.toLocaleString()).join(", ")}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {forecasts.length} metrics tracked
      </div>
    </div>
  );
}
