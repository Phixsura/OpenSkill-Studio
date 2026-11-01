"use client";
const SC: Record<string, string> = { green: "text-green-600", yellow: "text-yellow-600", red: "text-red-500" };
export function FleetElasticPanel({ status, nodes, activeShards, unassignedShards }: { status: string; nodes: number; activeShards: number; unassignedShards: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔍 ElasticSearch</h3>
    <div className={`text-lg font-bold ${SC[status] ?? ""}`}>{status.toUpperCase()}</div>
    <div className="text-xs text-gray-400">{nodes} nodes · {activeShards} shards · {unassignedShards} unassigned</div>
  </div>);
}
