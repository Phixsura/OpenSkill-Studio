"use client";
export function FleetAiPlatObsV4Panel({ systems, active, metrics, traces, logs, cardinality }: { systems: number; active: number; metrics: number; traces: number; logs: number; cardinality: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Observability v4</h3>
    <div className="text-sm">{active}/{systems} active · {metrics.toLocaleString()} metrics · {traces.toLocaleString()} traces · {logs.toLocaleString()} logs</div>
  </div>);
}
