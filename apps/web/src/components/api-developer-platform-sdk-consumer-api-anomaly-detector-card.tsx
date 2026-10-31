"use client";

import { useState } from "react";

interface AnomalyInfo { metric: string; value: number; zScore: number; type: string; severity: string; }

const SEV_COLOR: Record<string, string> = {
  critical: "text-red-600 dark:text-red-400",
  high: "text-orange-600 dark:text-orange-400",
  medium: "text-amber-600 dark:text-amber-400",
};

export default function AnomalyDetectorCard() {
  const [anomalies] = useState<AnomalyInfo[]>([
    { metric: "latency_p99", value: 2500, zScore: 4.2, type: "spike", severity: "critical" },
    { metric: "error_rate", value: 12.5, zScore: 3.1, type: "spike", severity: "high" },
    { metric: "request_count", value: 150, zScore: -2.8, type: "dip", severity: "medium" },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Anomaly Detector</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Statistical anomaly detection with alerting</p>

      <div className="mt-4 space-y-2">
        {anomalies.map((a) => (
          <div key={a.metric} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div>
              <span className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{a.metric}</span>
              <span className="ml-2 text-xs text-zinc-400">{a.type} (z={a.zScore})</span>
            </div>
            <span className={`text-xs font-medium ${SEV_COLOR[a.severity]}`}>{a.severity}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {anomalies.length} anomalies detected
      </div>
    </div>
  );
}
