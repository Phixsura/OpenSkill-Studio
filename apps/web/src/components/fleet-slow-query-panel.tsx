"use client";
export function FleetSlowQueryPanel({ total, slow, verySlow, needsAttention }: { total: number; slow: number; verySlow: number; needsAttention: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐌 Slow Queries</h3>
    <div className="text-sm">{slow} slow · {verySlow} very slow of {total}</div>
    {needsAttention && <span className="text-xs text-red-500">🚨 Query optimization needed</span>}
  </div>);
}
