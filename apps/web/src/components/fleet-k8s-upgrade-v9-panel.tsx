"use client";
export function FleetK8sUpgradeV9Panel({ clusters, current }: { clusters: number; current: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ K8s Upgrade v9</h3>
    <div className="text-sm">{clusters} clusters · {current} current</div>
  </div>);
}
