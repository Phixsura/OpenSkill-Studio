"use client";
export function FleetClusterEtcdV9Panel({ clusters, dbSize }: { clusters: number; dbSize: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Cluster etcd v9</h3>
    <div className="text-sm">{clusters} clusters · {dbSize} MB db</div>
  </div>);
}
