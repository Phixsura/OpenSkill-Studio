"use client";
export function FleetNsCountPanel({ total, active, empty, needsCleanup }: { total: number; active: number; empty: number; needsCleanup: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📁 Namespaces</h3>
    <div className="text-sm">{active} active · {empty} empty of {total}</div>
    {needsCleanup && <span className="text-xs text-yellow-600">🧹 Cleanup recommended</span>}
  </div>);
}
