"use client";
export function FleetWidPanel({ total, workloadIdentity, saKeys, modern }: { total: number; workloadIdentity: number; saKeys: number; modern: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🆔 Workload Identity</h3>
    <div className="text-sm">{workloadIdentity}/{total} using WI</div>
    {!modern && <span className="text-xs text-yellow-600">⚠️ {saKeys} still using SA keys</span>}
  </div>);
}
