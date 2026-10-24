"use client";
export function FleetCbStatusPanel({ total, open, halfOpen, closed, healthy }: { total: number; open: number; halfOpen: number; closed: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Circuit Breakers</h3>
    <div className="text-sm">🟢 {closed} closed · 🟡 {halfOpen} half-open · 🔴 {open} open</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {open} circuits open</span>}
  </div>);
}
