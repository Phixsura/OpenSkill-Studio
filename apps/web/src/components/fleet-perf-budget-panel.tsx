"use client";
export function FleetPerfBudgetPanel({ total, withinBudget, overBudget, compliant }: { total: number; withinBudget: number; overBudget: number; compliant: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Perf Budget</h3>
    {compliant ? <span className="text-xs text-green-600">✅ All {total} pages within budget</span>
     : <span className="text-xs text-yellow-600">⚠️ {overBudget}/{total} over performance budget</span>}
  </div>);
}
