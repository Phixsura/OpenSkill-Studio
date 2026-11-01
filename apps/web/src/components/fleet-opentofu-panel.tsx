"use client";
export function FleetOpentofuPanel({ total, clean, withChanges, totalResources }: { total: number; clean: number; withChanges: number; totalResources: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🟢 OpenTofu</h3>
    <div className="text-sm">{clean}/{total} clean · {totalResources} resources</div>
    {withChanges > 0 && <span className="text-xs text-yellow-600">⚠️ {withChanges} pending changes</span>}
  </div>);
}
