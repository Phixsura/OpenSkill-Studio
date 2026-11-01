"use client";
export function FleetEvictionPanel({ total, highRate }: { total: number; highRate: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚫 Pod Evictions</h3>
    <div className="text-sm">{total} evictions</div>
    {highRate && <span className="text-xs text-red-500">⚠️ High eviction rate</span>}
  </div>);
}
