"use client";
export function FleetChurnPanel({ churned, churnRate, netGrowth, healthy }: { churned: number; churnRate: number; netGrowth: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 Churn Rate</h3>
    <div className={`text-lg font-bold ${healthy ? "text-green-600" : "text-red-500"}`}>{churnRate}%</div>
    <div className="text-xs text-gray-400">{churned} churned · net {netGrowth >= 0 ? "+" : ""}{netGrowth}</div>
  </div>);
}
