"use client";
export function FleetMeshTelemPanel({ proxies, totalRps, avgLatency, errors, healthy }: { proxies: number; totalRps: number; avgLatency: number; errors: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Mesh Telemetry</h3>
    <div className="text-sm">{proxies} proxies · {totalRps.toLocaleString()} rps · {avgLatency}ms</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {errors} proxy errors</span>}
  </div>);
}
