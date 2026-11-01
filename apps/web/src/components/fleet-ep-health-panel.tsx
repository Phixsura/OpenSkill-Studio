"use client";
export function FleetEpHealthPanel({ total, up, degraded, down, availabilityPct }: { total: number; up: number; degraded: number; down: number; availabilityPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Endpoint Health</h3>
    <div className={`text-lg font-bold ${availabilityPct >= 99 ? "text-green-600" : "text-red-500"}`}>{availabilityPct}%</div>
    <div className="text-xs text-gray-400">🟢 {up} · 🟡 {degraded} · 🔴 {down}</div>
  </div>);
}
