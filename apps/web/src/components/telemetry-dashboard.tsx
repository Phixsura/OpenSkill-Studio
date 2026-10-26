"use client";

import { useState } from "react";

interface TelemetryStats {
  totalRecords: number;
  droppedBySampling: number;
  exported: Record<string, number>;
  configuredExtensions: number;
}

interface MetricAggregate {
  name: string;
  count: number;
  sum: number;
  avg: number;
  min: number;
  max: number;
}

interface TelemetryRecord {
  id: string;
  type: "metric" | "trace" | "log" | "event";
  name: string;
  value: number;
  tags: Record<string, string>;
}

const typeIcons: Record<string, string> = {
  metric: "📊", trace: "🔍", log: "📝", event: "⚡",
};

export function TelemetryDashboard({
  stats,
  aggregates,
  recentRecords,
  onFlush,
}: {
  stats: TelemetryStats;
  aggregates: MetricAggregate[];
  recentRecords: TelemetryRecord[];
  onFlush?: () => void;
}) {
  const [tab, setTab] = useState<"overview" | "metrics" | "recent">("overview");
  const acceptRate = stats.totalRecords + stats.droppedBySampling > 0
    ? Math.round(stats.totalRecords / (stats.totalRecords + stats.droppedBySampling) * 100) : 100;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📡 Telemetry</h2>
        <button onClick={onFlush} className="text-xs bg-red-600 text-white px-3 py-1 rounded-lg">Flush</button>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Records</span>
          <span className="font-bold">{stats.totalRecords.toLocaleString()}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Accept Rate</span>
          <span className="font-bold text-green-600">{acceptRate}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Dropped</span>
          <span className="font-bold text-yellow-600">{stats.droppedBySampling}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-xs text-gray-500 block">Extensions</span>
          <span className="font-bold">{stats.configuredExtensions}</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["overview", "metrics", "recent"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "overview" ? "Exports" : t === "metrics" ? "Aggregates" : "Recent"}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="space-y-1">
          {Object.entries(stats.exported).map(([target, count]) => (
            <div key={target} className="flex justify-between rounded-lg border dark:border-gray-700 p-2 text-sm">
              <span className="capitalize">{target}</span>
              <span className="font-bold">{count.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "metrics" && (
        <div className="space-y-1">
          {aggregates.map((m) => (
            <div key={m.name} className="rounded-lg border dark:border-gray-700 p-3">
              <code className="text-sm font-semibold">{m.name}</code>
              <div className="flex gap-3 text-xs text-gray-500 mt-1">
                <span>count: {m.count}</span>
                <span>avg: {m.avg}</span>
                <span>min: {m.min}</span>
                <span>max: {m.max}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "recent" && (
        <div className="space-y-1">
          {recentRecords.map((r) => (
            <div key={r.id} className="flex items-center gap-2 rounded-lg border dark:border-gray-700 p-2 text-xs">
              <span>{typeIcons[r.type]}</span>
              <code>{r.name}</code>
              <span className="text-gray-400">{r.value}</span>
              {Object.entries(r.tags).map(([k, v]) => (
                <span key={k} className="text-gray-400">{k}={v}</span>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
