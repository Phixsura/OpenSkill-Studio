"use client";
export function FleetDepFreshPanel({ total, outdated, critical, upToDate }: { total: number; outdated: number; critical: number; upToDate: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Dependency Freshness</h3>
    {upToDate ? <span className="text-xs text-green-600">✅ All {total} deps current</span>
     : <span className="text-xs text-yellow-600">⚠️ {outdated} outdated · {critical} critical</span>}
  </div>);
}
