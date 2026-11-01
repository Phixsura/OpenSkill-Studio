"use client";
export function FleetProgDelPanel({ total, inProgress, completed, paused }: { total: number; inProgress: number; completed: number; paused: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚀 Progressive Delivery</h3>
    <div className="text-sm">🔄 {inProgress} · ✅ {completed} · ⏸️ {paused}</div>
  </div>);
}
