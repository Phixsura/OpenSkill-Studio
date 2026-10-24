"use client";
export function FleetMulticlusterPanel({ total, healthy, degraded, down, allOk }: { total: number; healthy: number; degraded: number; down: number; allOk: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Multi-Cluster</h3>
    <div className="text-sm">🟢 {healthy} · 🟡 {degraded} · 🔴 {down} of {total}</div>
  </div>);
}
