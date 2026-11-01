"use client";
export function FleetGrpcPanel({ total, serving, notServing, avgLatency, healthy }: { total: number; serving: number; notServing: number; avgLatency: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 gRPC Health</h3>
    <div className="text-sm">{serving}/{total} serving · {avgLatency}ms avg</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {notServing} not serving</span>}
  </div>);
}
