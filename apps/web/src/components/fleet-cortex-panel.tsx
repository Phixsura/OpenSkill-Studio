"use client";
export function FleetCortexPanel({ clusters, healthy, activeSeries, ingestionRate }: { clusters: number; healthy: number; activeSeries: number; ingestionRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Cortex</h3>
    <div className="text-sm">{healthy}/{clusters} healthy · {activeSeries.toLocaleString()} series · {ingestionRate.toLocaleString()} sps</div>
  </div>);
}
