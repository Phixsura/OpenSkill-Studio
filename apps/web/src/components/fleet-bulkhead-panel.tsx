"use client";
export function FleetBulkheadPanel({ pools, active, max, rejected, utilPct, healthy }: { pools: number; active: number; max: number; rejected: number; utilPct: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Bulkhead</h3>
    <div className="text-sm">{active}/{max} threads ({utilPct}%) · {pools} pools</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {rejected} rejected</span>}
  </div>);
}
