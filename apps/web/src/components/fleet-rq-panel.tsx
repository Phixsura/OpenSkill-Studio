"use client";
export function FleetRqPanel({ total, overThreshold, healthy }: { total: number; overThreshold: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Resource Quotas</h3>
    {healthy ? <span className="text-xs text-green-600">✅ All {total} namespaces within quota</span>
     : <span className="text-xs text-yellow-600">⚠️ {overThreshold}/{total} over 80%</span>}
  </div>);
}
