"use client";
export function FleetClusterHealthV9Panel({ clusters, nodes }: { clusters: number; nodes: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Cluster Health v9</h3>
    <div className="text-sm">{clusters} clusters · {nodes} nodes</div>
  </div>);
}
