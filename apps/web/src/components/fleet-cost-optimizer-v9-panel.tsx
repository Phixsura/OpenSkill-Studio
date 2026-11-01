"use client";
export function FleetCostOptimizerV9Panel({ savings, applied }: { savings: number; applied: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💵 Cost Optimizer v9</h3>
    <div className="text-sm">${savings.toLocaleString()}/mo savings · {applied} applied</div>
  </div>);
}
