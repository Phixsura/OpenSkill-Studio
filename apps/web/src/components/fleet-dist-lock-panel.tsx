"use client";
export function FleetDistLockPanel({ activeLocks, contention, deadlocks, healthy }: { activeLocks: number; contention: number; deadlocks: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 Dist Locks</h3>
    <div className="text-sm">{activeLocks} active · {contention} contentions · {deadlocks} deadlocks</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ Lock issues!</span>}
  </div>);
}
