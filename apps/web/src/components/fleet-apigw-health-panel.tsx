"use client";
export function FleetApigwHealthPanel({ gateways, healthy, totalRps, avgLatency, allHealthy }: { gateways: number; healthy: number; totalRps: number; avgLatency: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚪 API Gateway</h3>
    <div className="text-sm">{healthy}/{gateways} healthy · {totalRps.toLocaleString()} rps · {avgLatency}ms</div>
  </div>);
}
