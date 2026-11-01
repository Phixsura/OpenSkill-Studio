"use client";
export function MeshErrBudgetPanel({ exhausted, total, allWithin }: { exhausted: number; total: number; allWithin: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Mesh Error Budget</h3>
    <span className={`text-xs ${allWithin ? "text-green-600" : "text-red-500"}`}>{allWithin ? "✅ All within budget" : `❌ ${exhausted} exhausted`}</span>
  </div>);
}
