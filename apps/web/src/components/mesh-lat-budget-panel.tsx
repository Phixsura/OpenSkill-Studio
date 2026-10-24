"use client";
export function MeshLatBudgetPanel({ overBudget, total, allWithin }: { overBudget: number; total: number; allWithin: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ Mesh Latency Budget</h3>
    <span className={`text-xs ${allWithin ? "text-green-600" : "text-yellow-600"}`}>{overBudget}/{total} over budget</span>
  </div>);
}
