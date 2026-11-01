"use client";
export function FleetAiFinalStatusPanel({ total, operational, degraded, down, uptime, status }: { total: number; operational: number; degraded: number; down: number; uptime: number; status: string; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏠 AI Final Status</h3>
    <div className="text-sm">🟢 {operational} · 🟡 {degraded} · 🔴 {down} of {total} · {uptime}% uptime</div>
    <div className="text-xs mt-1 font-bold">{status}</div>
  </div>);
}
