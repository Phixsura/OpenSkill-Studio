"use client";
export function FleetClusterUpgradeV9Panel({ clusters, upgraded }: { clusters: number; upgraded: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Cluster Upgrade v9</h3>
    <div className="text-sm">{clusters} clusters · {upgraded} upgraded</div>
  </div>);
}
