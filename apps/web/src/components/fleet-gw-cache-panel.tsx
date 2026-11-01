"use client";
export function FleetGwCachePanel({ total, cached, hitRate, effective }: { total: number; cached: number; hitRate: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Gateway Cache</h3>
    <div className="text-sm">{cached}/{total} cached · {hitRate}% hit rate</div>
    {effective && <span className="text-xs text-green-600">✅ Effective caching</span>}
  </div>);
}
