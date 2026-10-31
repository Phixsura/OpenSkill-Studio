"use client";
export function FleetAiModelObsV2Panel({ systems, active, models, metrics, traces, logs }: { systems: number; active: number; models: number; metrics: number; traces: number; logs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Model Observability v2</h3>
    <div className="text-sm">{active}/{systems} active · {models} models · {metrics.toLocaleString()} metrics · {traces.toLocaleString()} traces</div>
  </div>);
}
