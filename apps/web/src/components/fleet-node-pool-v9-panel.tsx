"use client";
export function FleetNodePoolV9Panel({ pools, nodes }: { pools: number; nodes: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">☸️ Node Pool v9</h3>
    <div className="text-sm">{pools} pools · {nodes} nodes</div>
  </div>);
}
