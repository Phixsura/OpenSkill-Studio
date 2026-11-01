"use client";
export function FleetVictoriametricsPanel({ nodes, healthy, rowsPerSec, storageGb }: { nodes: number; healthy: number; rowsPerSec: number; storageGb: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 VictoriaMetrics</h3>
    <div className="text-sm">{healthy}/{nodes} healthy · {rowsPerSec.toLocaleString()} rows/s · {storageGb}GB</div>
  </div>);
}
