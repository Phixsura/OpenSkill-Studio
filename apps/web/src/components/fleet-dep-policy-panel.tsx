"use client";
export function FleetDepPolicyPanel({ total, autoUpdate, modern }: { total: number; autoUpdate: number; modern: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📦 Dep Update Policy</h3>
    <div className="text-sm">{autoUpdate}/{total} auto-update</div>
    {!modern && <span className="text-xs text-yellow-600">⚠️ Not all repos auto-update</span>}
  </div>);
}
