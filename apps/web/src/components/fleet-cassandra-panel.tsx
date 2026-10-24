"use client";
export function FleetCassandraPanel({ nodes, up, down, totalLoad }: { nodes: number; up: number; down: number; totalLoad: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">👁️ Cassandra</h3>
    <div className="text-sm">{up}/{nodes} up · {totalLoad}GB load</div>
    {down > 0 && <span className="text-xs text-red-500">🚨 {down} nodes down</span>}
  </div>);
}
