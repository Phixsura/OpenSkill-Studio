"use client";
export function FleetAiClusterMgrPanel({ managers, active, clusters, nodes, utilization }: { managers: number; active: number; clusters: number; nodes: number; utilization: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ AI Cluster Manager</h3>
    <div className="text-sm">{active}/{managers} active · {clusters} clusters · {nodes.toLocaleString()} nodes · {utilization}% util</div>
  </div>);
}
