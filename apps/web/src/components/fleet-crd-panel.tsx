"use client";
export function FleetCrdPanel({ total, healthy, stale, allEstablished }: { total: number; healthy: number; stale: number; allEstablished: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧩 CRDs</h3>
    <div className="text-sm">{healthy}/{total} established · {stale} stale</div>
    {!allEstablished && <span className="text-xs text-yellow-600">⚠️ Not all CRDs established</span>}
  </div>);
}
