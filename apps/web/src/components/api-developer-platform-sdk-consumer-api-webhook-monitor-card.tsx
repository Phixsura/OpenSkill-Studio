"use client";

import { useState } from "react";

interface MonitorInfo { webhookId: string; status: string; successRate: number; avgLatency: number; }

const STATUS_COLOR: Record<string, string> = {
  healthy: "bg-green-500",
  degraded: "bg-amber-500",
  unhealthy: "bg-red-500",
};

export default function WebhookMonitorCard() {
  const [webhooks] = useState<MonitorInfo[]>([
    { webhookId: "wh-orders", status: "healthy", successRate: 99.8, avgLatency: 42 },
    { webhookId: "wh-users", status: "degraded", successRate: 94.5, avgLatency: 180 },
    { webhookId: "wh-alerts", status: "unhealthy", successRate: 72.0, avgLatency: 500 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Webhook Monitor</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Real-time webhook health monitoring</p>

      <div className="mt-4 space-y-2">
        {webhooks.map((w) => (
          <div key={w.webhookId} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${STATUS_COLOR[w.status]}`} />
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{w.webhookId}</span>
            </div>
            <div className="text-xs text-zinc-500">
              {w.successRate}% · {w.avgLatency}ms
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {webhooks.filter((w) => w.status === "healthy").length}/{webhooks.length} healthy
      </div>
    </div>
  );
}
