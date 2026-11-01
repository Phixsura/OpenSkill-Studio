"use client";
export function FleetAiModelEpV3Panel({ endpoints, active, rps, p50, p99 }: { endpoints: number; active: number; rps: number; p50: number; p99: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 AI Model Endpoint v3</h3>
    <div className="text-sm">{active}/{endpoints} active · {rps.toLocaleString()} RPS · p50 {p50}ms · p99 {p99}ms</div>
  </div>);
}
