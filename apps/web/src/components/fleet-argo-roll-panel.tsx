"use client";
export function FleetArgoRollPanel({ total, healthy, paused, degraded }: { total: number; healthy: number; paused: number; degraded: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔄 Argo Rollouts</h3>
    <div className="text-sm">{healthy}✅ {paused}⏸️ {degraded}⚠️ of {total}</div>
  </div>);
}
