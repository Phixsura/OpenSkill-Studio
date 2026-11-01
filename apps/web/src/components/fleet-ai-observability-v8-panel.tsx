"use client";
export function FleetAiObservabilityV8Panel({ stacks, active, metrics, traces, logs }: { stacks: number; active: number; metrics: number; traces: number; logs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 AI Observability v8</h3>
    <div className="text-sm">{active}/{stacks} active · {metrics.toLocaleString()} metrics · {traces.toLocaleString()} traces · {logs.toLocaleString()} logs</div>
  </div>);
}
