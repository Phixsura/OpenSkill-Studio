"use client";

import { useState } from "react";

interface MetricEntry {
  name: string;
  type: "counter" | "gauge" | "histogram";
  value: number;
  labels?: Record<string, string>;
  histogramStats?: { count: number; avg: number; p50: number; p99: number };
}

const typeColors: Record<string, string> = {
  counter: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
  gauge: "bg-green-100 text-green-700 dark:bg-green-900/30",
  histogram: "bg-purple-100 text-purple-700 dark:bg-purple-900/30",
};

export function MetricsExporterPanel({
  metrics,
  extensionName,
  onExport,
}: {
  metrics: MetricEntry[];
  extensionName: string;
  onExport?: () => void;
}) {
  const [filter, setFilter] = useState<string>("all");

  const filtered = filter === "all" ? metrics : metrics.filter((m) => m.type === filter);
  const counters = metrics.filter((m) => m.type === "counter").length;
  const gauges = metrics.filter((m) => m.type === "gauge").length;
  const histograms = metrics.filter((m) => m.type === "histogram").length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📈 {extensionName} Metrics</h2>
        <button onClick={onExport} className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">Export</button>
      </div>

      <div className="flex gap-2 text-xs">
        {[
          { key: "all", label: `All (${metrics.length})` },
          { key: "counter", label: `Counters (${counters})` },
          { key: "gauge", label: `Gauges (${gauges})` },
          { key: "histogram", label: `Histograms (${histograms})` },
        ].map((f) => (
          <button key={f.key} onClick={() => setFilter(f.key)}
            className={`px-2.5 py-1 rounded-full ${filter === f.key ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {f.label}
          </button>
        ))}
      </div>

      <div className="space-y-1">
        {filtered.map((m, i) => (
          <div key={`${m.name}-${i}`} className="rounded-lg border dark:border-gray-700 p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <code className="text-sm font-semibold">{m.name}</code>
                <span className={`text-xs px-1.5 py-0.5 rounded ${typeColors[m.type]}`}>{m.type}</span>
                {m.labels && Object.entries(m.labels).map(([k, v]) => (
                  <span key={k} className="text-xs text-gray-400">{k}={v}</span>
                ))}
              </div>
              <span className="font-mono text-sm font-bold">{m.value}</span>
            </div>
            {m.histogramStats && (
              <div className="flex gap-4 mt-1 text-xs text-gray-500">
                <span>count: {m.histogramStats.count}</span>
                <span>avg: {m.histogramStats.avg}ms</span>
                <span>p50: {m.histogramStats.p50}ms</span>
                <span>p99: {m.histogramStats.p99}ms</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
