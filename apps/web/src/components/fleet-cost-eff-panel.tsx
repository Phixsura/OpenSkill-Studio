"use client";
const GC: Record<string, string> = { A: "text-green-600", B: "text-blue-500", C: "text-yellow-600" };
export function FleetCostEffPanel({ ratio, grade, revenue, infraCost }: { ratio: number; grade: string; revenue: number; infraCost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Efficiency</h3>
    <div className={`text-lg font-bold ${GC[grade] ?? ""}`}>{ratio}x — {grade}</div>
    <div className="text-xs text-gray-400">${revenue.toLocaleString()} rev / ${infraCost.toLocaleString()} cost</div>
  </div>);
}
