"use client";
export function FleetGwMeshPanel({ gateways, healthy, totalRps, avgP50, allHealthy }: { gateways: number; healthy: number; totalRps: number; avgP50: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 Gateway Mesh</h3>
    <div className="text-sm">{healthy}/{gateways} healthy · {totalRps.toLocaleString()} rps · p50 {avgP50}ms</div>
  </div>);
}
