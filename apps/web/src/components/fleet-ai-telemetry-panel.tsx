"use client";
export function FleetAiTelemetryPanel({ collectors, active, metrics, traces, logs }: { collectors: number; active: number; metrics: number; traces: number; logs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Telemetry</h3>
    <div className="text-sm">{active}/{collectors} active · {metrics.toLocaleString()} metrics · {traces.toLocaleString()} traces · {logs.toLocaleString()} logs</div>
  </div>);
}
