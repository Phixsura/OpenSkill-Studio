"use client";
export function FleetMemcachedPanel({ nodes, alive, items, hitRate }: { nodes: number; alive: number; items: number; hitRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧊 Memcached</h3>
    <div className="text-sm">{alive}/{nodes} alive · {items.toLocaleString()} items · {hitRate}% hit</div>
  </div>);
}
