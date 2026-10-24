"use client";
export function FleetPrometheusPanel({ instances, healthy, totalSeries, storageGb, allHealthy }: { instances: number; healthy: number; totalSeries: number; storageGb: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Prometheus</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {totalSeries.toLocaleString()} series · {storageGb}GB</div>
    {!allHealthy && <span className="text-xs text-red-500">⚠️ Unhealthy instances</span>}
  </div>);
}
