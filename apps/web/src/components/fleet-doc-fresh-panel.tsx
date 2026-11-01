"use client";
export function FleetDocFreshPanel({ total, fresh, stale, freshnessPct }: { total: number; fresh: number; stale: number; freshnessPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📖 Doc Freshness</h3>
    <div className="text-sm">{fresh}/{total} fresh ({freshnessPct}%)</div>
    {stale > 0 && <span className="text-xs text-yellow-600">⚠️ {stale} stale docs</span>}
  </div>);
}
