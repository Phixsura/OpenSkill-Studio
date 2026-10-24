"use client";
export function FleetApiCostTrackingV9Panel({ apis, cost }: { apis: number; cost: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 API Cost Tracking v9</h3>
    <div className="text-sm">{apis} APIs · ${cost.toLocaleString()}/mo</div>
  </div>);
}
