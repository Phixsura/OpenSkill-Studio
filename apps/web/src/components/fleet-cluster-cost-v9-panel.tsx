"use client";
export function FleetClusterCostV9Panel({ clusters, total }: { clusters: number; total: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 Cluster Cost v9</h3>
    <div className="text-sm">{clusters} clusters · ${total.toLocaleString()}/mo</div>
  </div>);
}
