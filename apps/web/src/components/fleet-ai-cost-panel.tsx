"use client";
export function FleetAiCostPanel({ totalMonthly, gpuCost, inferenceCost, savings }: { totalMonthly: number; gpuCost: number; inferenceCost: number; savings: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Cost</h3>
    <div className="text-sm">${totalMonthly.toLocaleString()}/mo · GPU ${gpuCost.toLocaleString()} · Inference ${inferenceCost.toLocaleString()}</div>
    {savings > 0 && <span className="text-xs text-green-600">💰 ${savings.toLocaleString()} savings available</span>}
  </div>);
}
