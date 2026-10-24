"use client";
export function FleetCostCenterV9Panel({ centers, spend }: { centers: number; spend: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cost Center v9</h3>
    <div className="text-sm">{centers} centers · ${spend.toLocaleString()}/mo</div>
  </div>);
}
