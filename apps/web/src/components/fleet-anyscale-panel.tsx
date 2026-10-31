"use client";
export function FleetAnyscalePanel({ clusters, running, nodes, activeJobs }: { clusters: number; running: number; nodes: number; activeJobs: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔆 Anyscale</h3>
    <div className="text-sm">{running}/{clusters} running · {nodes} nodes · {activeJobs} jobs</div>
  </div>);
}
