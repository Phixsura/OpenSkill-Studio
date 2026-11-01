"use client";
export function FleetEdaPanel({ topics, healthy, unhealthy, totalEps, allHealthy }: { topics: number; healthy: number; unhealthy: number; totalEps: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Event-Driven</h3>
    <div className="text-sm">{healthy}/{topics} healthy · {totalEps.toLocaleString()} eps</div>
    {!allHealthy && <span className="text-xs text-yellow-600">⚠️ {unhealthy} lagging topics</span>}
  </div>);
}
