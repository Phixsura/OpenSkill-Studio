"use client";
export function FleetClusterFederationV9Panel({ clusters, federated }: { clusters: number; federated: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌐 Cluster Federation v9</h3>
    <div className="text-sm">{clusters} clusters · {federated} federated</div>
  </div>);
}
