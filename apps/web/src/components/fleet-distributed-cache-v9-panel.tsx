"use client";
export function FleetDistributedCacheV9Panel({ nodes, hitRate }: { nodes: number; hitRate: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Distributed Cache v9</h3>
    <div className="text-sm">{nodes} nodes · {hitRate}% hit rate</div>
  </div>);
}
