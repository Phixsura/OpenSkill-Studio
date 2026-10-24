"use client";
const TC: Record<string, string> = { increasing: "text-red-500", decreasing: "text-green-600", stable: "text-blue-500" };
export function FleetCostTrendPanel({ trend, changePct, latest }: { trend: string; changePct: number; latest: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 Cost Trend</h3>
    <div className={`text-lg font-bold ${TC[trend] ?? ""}`}>{trend} ({changePct > 0 ? "+" : ""}{changePct}%)</div>
    <div className="text-xs text-gray-400">${latest.toLocaleString()}/mo</div>
  </div>);
}
