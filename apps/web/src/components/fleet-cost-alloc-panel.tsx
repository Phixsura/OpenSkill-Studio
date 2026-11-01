"use client";
export function FleetCostAllocPanel({ totalCost, topSpender }: { totalCost: number; topSpender: string | null; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Allocation</h3>
    <div className="text-sm">${totalCost.toLocaleString()} total</div>
    {topSpender && <div className="text-xs text-blue-500">Top: {topSpender}</div>}
  </div>);
}
