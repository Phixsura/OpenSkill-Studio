"use client";
export function FleetInitCtrPanel({ total, withInit, failedInit, healthy }: { total: number; withInit: number; failedInit: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔧 Init Containers</h3>
    <div className="text-sm">{withInit}/{total} with init containers</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {failedInit} init failures</span>}
  </div>);
}
