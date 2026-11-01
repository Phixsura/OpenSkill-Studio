"use client";
export function FleetAiModelPerfPanel({ trackers, active, models, metrics, alerts }: { trackers: number; active: number; models: number; metrics: number; alerts: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 AI Model Performance</h3>
    <div className="text-sm">{active}/{trackers} active · {models} models · {metrics.toLocaleString()} metrics · {alerts} alerts</div>
  </div>);
}
