"use client";
export function FleetTempoPanel({ instances, healthy, tracesPerSec, minRetention, allHealthy }: { instances: number; healthy: number; tracesPerSec: number; minRetention: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🎵 Tempo</h3>
    <div className="text-sm">{healthy}/{instances} healthy · {tracesPerSec.toLocaleString()} traces/s · {minRetention}d retention</div>
  </div>);
}
