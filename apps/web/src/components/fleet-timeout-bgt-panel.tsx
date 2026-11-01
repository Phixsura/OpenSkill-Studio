"use client";
export function FleetTimeoutBgtPanel({ chains, overBudget, avgUtil, healthy }: { chains: number; overBudget: number; avgUtil: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Timeout Budget</h3>
    <div className="text-sm">{chains} chains · {avgUtil}% avg util</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ {overBudget} over budget</span>}
  </div>);
}
