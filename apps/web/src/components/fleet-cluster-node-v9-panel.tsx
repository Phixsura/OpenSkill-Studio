"use client";
export function FleetClusterNodeV9Panel({ nodes, ready }: { nodes: number; ready: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Cluster Node v9</h3>
    <div className="text-sm">{nodes} nodes · {ready} ready</div>
  </div>);
}
