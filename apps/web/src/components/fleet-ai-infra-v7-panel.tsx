"use client";
export function FleetAiInfraV7Panel({ systems, active, clusters, nodes, gpus, storage }: { systems: number; active: number; clusters: number; nodes: number; gpus: number; storage: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏗️ AI Infrastructure v7</h3>
    <div className="text-sm">{active}/{systems} active · {clusters} clusters · {nodes.toLocaleString()} nodes · {gpus.toLocaleString()} GPUs · {storage}PB</div>
  </div>);
}
