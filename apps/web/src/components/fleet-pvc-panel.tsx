"use client";
export function FleetPvcPanel({ total, bound, pending, lost, healthy }: { total: number; bound: number; pending: number; lost: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💿 PVCs</h3>
    <div className="text-sm">🟢 {bound} bound · 🟡 {pending} pending · 🔴 {lost} lost</div>
  </div>);
}
