"use client";
export function FleetSpannerPanel({ instances, ready, nodes, cpuPct }: { instances: number; ready: number; nodes: number; cpuPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔷 Spanner</h3>
    <div className="text-sm">{ready}/{instances} ready · {nodes} nodes · {cpuPct}% CPU</div>
  </div>);
}
