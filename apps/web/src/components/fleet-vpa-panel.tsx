"use client";
export function FleetVpaPanel({ total, autoMode, monthlySavings, effective }: { total: number; autoMode: number; monthlySavings: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📏 VPA</h3>
    <div className="text-sm">{autoMode}/{total} auto · ${monthlySavings.toLocaleString()}/mo savings</div>
    {effective && <span className="text-xs text-green-600">💰 Saving costs</span>}
  </div>);
}
