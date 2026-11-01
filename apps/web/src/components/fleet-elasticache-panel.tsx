"use client";
export function FleetElasticachePanel({ clusters, available, nodes, memoryPct }: { clusters: number; available: number; nodes: number; memoryPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ ElastiCache</h3>
    <div className="text-sm">{available}/{clusters} available · {nodes} nodes · {memoryPct}% mem</div>
  </div>);
}
