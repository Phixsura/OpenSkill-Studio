"use client";

import { useState } from "react";

interface MetricInfo { name: string; type: string; samples: number; }

export default function MetricsExporterCard() {
  const [metrics] = useState<MetricInfo[]>([
    { name: "http_requests_total", type: "counter", samples: 45200 },
    { name: "api_latency_seconds", type: "histogram", samples: 45200 },
    { name: "active_connections", type: "gauge", samples: 1250 },
    { name: "error_rate", type: "gauge", samples: 890 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Metrics Exporter</h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Prometheus-format metrics export</p>

      <div className="mt-4 space-y-2">
        {metrics.map((m) => (
          <div key={m.name} className="flex items-center justify-between rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-700">
            <code className="text-sm text-zinc-800 dark:text-zinc-200">{m.name}</code>
            <div className="flex items-center gap-2 text-xs">
              <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400">{m.type}</span>
              <span className="text-zinc-400">{m.samples.toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">{metrics.length} metrics exported</div>
    </div>
  );
}
