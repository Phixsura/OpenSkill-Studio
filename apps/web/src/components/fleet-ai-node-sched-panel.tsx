"use client";
export function FleetAiNodeSchedPanel({ schedulers, active, nodes, placements, preemptions }: { schedulers: number; active: number; nodes: number; placements: number; preemptions: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📍 AI Node Scheduler</h3>
    <div className="text-sm">{active}/{schedulers} active · {nodes.toLocaleString()} nodes · {placements.toLocaleString()} placements · {preemptions} preemptions</div>
  </div>);
}
