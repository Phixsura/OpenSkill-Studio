"use client";
export function FleetJaegerPanel({ collectors, healthy, spansPerSec, storageGb, allHealthy }: { collectors: number; healthy: number; spansPerSec: number; storageGb: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 Jaeger</h3>
    <div className="text-sm">{healthy}/{collectors} collectors · {spansPerSec.toLocaleString()} spans/s · {storageGb}GB</div>
  </div>);
}
