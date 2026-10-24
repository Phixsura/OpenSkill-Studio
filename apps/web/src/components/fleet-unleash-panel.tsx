"use client";
export function FleetUnleashPanel({ total, enabled, stale, impressions }: { total: number; enabled: number; stale: number; impressions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔓 Unleash</h3>
    <div className="text-sm">{enabled}/{total} enabled · {impressions.toLocaleString()} impressions/24h</div>
    {stale > 0 && <span className="text-xs text-yellow-600">🧹 {stale} stale toggles</span>}
  </div>);
}
