"use client";
export function FleetAiFuncRegPanel({ registries, active, functions, calls, latency }: { registries: number; active: number; functions: number; calls: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 AI Function Registry</h3>
    <div className="text-sm">{active}/{registries} active · {functions} functions · {calls.toLocaleString()} calls · {latency}ms</div>
  </div>);
}
