"use client";
export function FleetMimirPanel({ clusters, healthy, totalSeries, samplesPerSec, allHealthy }: { clusters: number; healthy: number; totalSeries: number; samplesPerSec: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Mimir</h3>
    <div className="text-sm">{healthy}/{clusters} healthy · {totalSeries.toLocaleString()} series · {samplesPerSec.toLocaleString()} sps</div>
  </div>);
}
