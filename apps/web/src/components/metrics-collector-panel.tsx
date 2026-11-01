"use client";

import { useState } from "react";

interface MetricAggregate {
  name: string;
  count: number;
  avg: number;
  min: number;
  max: number;
  p95: number;
}

interface ThresholdAlert {
  metric: string;
  current: number;
  threshold: number;
  exceeded: boolean;
}

export function MetricsCollectorPanel({
  currentValues,
  aggregates,
  alerts,
  metricNames,
  onRefresh,
}: {
  currentValues: Record<string, number>;
  aggregates: MetricAggregate[];
  alerts: ThresholdAlert[];
  metricNames: string[];
  onRefresh?: () => void;
}) {
  const [tab, setTab] = useState<"current" | "aggregates" | "alerts">("current");
  const activeAlerts = alerts.filter((a) => a.exceeded).length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 Sandbox Metrics</h2>
        <div className="flex items-center gap-2">
          {activeAlerts > 0 && (
            <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">{activeAlerts} alerts</span>
          )}
          <button onClick={onRefresh} className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Refresh</button>
        </div>
      </div>

      <div className="flex gap-1">
        {(["current", "aggregates", "alerts"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "current" ? "Live" : t === "aggregates" ? "Aggregates" : `Alerts (${activeAlerts})`}
          </button>
        ))}
      </div>

      {tab === "current" && (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          {Object.entries(currentValues).map(([name, value]) => (
            <div key={name} className="rounded-lg border dark:border-gray-700 p-3 text-center">
              <span className="text-xs text-gray-500 block">{name}</span>
              <span className="text-lg font-bold">{value}</span>
            </div>
          ))}
        </div>
      )}

      {tab === "aggregates" && (
        <div className="space-y-1">
          {aggregates.map((m) => (
            <div key={m.name} className="rounded-lg border dark:border-gray-700 p-3">
              <code className="text-sm font-semibold">{m.name}</code>
              <div className="flex gap-3 text-xs text-gray-500 mt-1">
                <span>avg: <b>{m.avg}</b></span>
                <span>min: {m.min}</span>
                <span>max: {m.max}</span>
                <span>p95: <b>{m.p95}</b></span>
                <span>n={m.count}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "alerts" && (
        <div className="space-y-1">
          {alerts.map((a) => (
            <div key={a.metric} className={`rounded-lg border-l-4 p-3 ${a.exceeded ? "border-red-500 bg-red-50 dark:bg-red-900/10" : "border-green-400 bg-green-50 dark:bg-green-900/10"}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{a.metric}</span>
                <span className={`text-sm font-bold ${a.exceeded ? "text-red-600" : "text-green-600"}`}>
                  {a.current} / {a.threshold}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
