"use client";
export function FleetCostSumPanel({ totalCost, avgCost, services }: { totalCost: number; avgCost: number; services: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Fleet Cost</h3>
    <span className="text-xs text-gray-400">${totalCost.toLocaleString()} total · ${avgCost}/svc · {services} services</span>
  </div>);
}
