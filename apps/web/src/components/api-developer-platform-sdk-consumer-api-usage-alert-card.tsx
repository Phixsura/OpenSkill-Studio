"use client";

import { useState } from "react";

interface AlertInfo { metric: string; level: string; value: number; threshold: number; }

const LVL_COLOR: Record<string, string> = {
  info: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function UsageAlertCard() {
  const [alerts] = useState<AlertInfo[]>([
    { metric: "error_rate", level: "critical", value: 12.5, threshold: 5.0 },
    { metric: "latency_p99", level: "warning", value: 450, threshold: 300 },
    { metric: "request_count", level: "info", value: 9500, threshold: 10000 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Usage Alerts</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Usage threshold alerting with escalation</p>

      <div className="mt-4 space-y-2">
        {alerts.map((a) => (
          <div key={a.metric} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${LVL_COLOR[a.level]}`}>{a.level}</span>
              <span className="text-sm text-zinc-800 dark:text-zinc-200">{a.metric}</span>
            </div>
            <span className="text-xs text-zinc-500">{a.value} / {a.threshold}</span>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{alerts.length} alerts fired</div>
    </div>
  );
}
