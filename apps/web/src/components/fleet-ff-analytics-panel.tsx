"use client";
export function FleetFfAnalyticsPanel({ totalFlags, enabled, totalEvals, stale }: { totalFlags: number; enabled: number; totalEvals: number; stale: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚩 Flag Analytics</h3>
    <div className="text-sm">{enabled}/{totalFlags} enabled · {totalEvals.toLocaleString()} evals/24h</div>
    {stale > 0 && <span className="text-xs text-yellow-600">⚠️ {stale} stale flags</span>}
  </div>);
}
