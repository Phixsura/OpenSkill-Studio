"use client";
export function FleetCostAllocationV9Panel({ allocations, total }: { allocations: number; total: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Allocation v9</h3>
    <div className="text-sm">{allocations} allocations · ${total.toLocaleString()}/mo</div>
  </div>);
}
