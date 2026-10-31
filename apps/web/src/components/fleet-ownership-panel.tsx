"use client";
export function FleetOwnershipPanel({ total, owned, unowned, coveragePct }: { total: number; owned: number; unowned: number; coveragePct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👤 Code Ownership</h3>
    <div className="text-sm">{owned}/{total} owned ({coveragePct}%)</div>
    {unowned > 0 && <span className="text-xs text-yellow-600">⚠️ {unowned} unowned files</span>}
  </div>);
}
