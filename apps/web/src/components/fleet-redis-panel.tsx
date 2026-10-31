"use client";
export function FleetRedisPanel({ nodes, masters, replicas, totalKeys, memoryPct, healthy }: { nodes: number; masters: number; replicas: number; totalKeys: number; memoryPct: number; healthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔴 Redis</h3>
    <div className="text-sm">{masters}M/{replicas}R · {totalKeys.toLocaleString()} keys · {memoryPct}% mem</div>
    {!healthy && <span className="text-xs text-red-500">⚠️ High memory usage</span>}
  </div>);
}
