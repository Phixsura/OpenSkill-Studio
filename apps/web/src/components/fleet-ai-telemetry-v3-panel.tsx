"use client";
export function FleetAiTelemetryV3Panel({ collectors, active, metrics, traces, logs, storage }: { collectors: number; active: number; metrics: number; traces: number; logs: number; storage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Telemetry v3</h3>
    <div className="text-sm">{active}/{collectors} active · {metrics.toLocaleString()} metrics · {traces.toLocaleString()} traces · {storage}GB</div>
  </div>);
}
