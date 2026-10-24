"use client";
export function FleetApiConsistPanel({ total, consistent, inconsistent, score }: { total: number; consistent: number; inconsistent: number; score: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📐 API Consistency</h3>
    <div className="text-sm">{consistent}/{total} consistent ({score}%)</div>
    {inconsistent > 0 && <span className="text-xs text-yellow-600">⚠️ {inconsistent} inconsistent</span>}
  </div>);
}
