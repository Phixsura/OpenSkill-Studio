"use client";
export function FleetLokiPanel({ instances, healthy, ingestionRate, queryAvg, allHealthy }: { instances: number; healthy: number; ingestionRate: number; queryAvg: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Loki</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {ingestionRate}MB/s · query {queryAvg}ms</div>
  </div>);
}
