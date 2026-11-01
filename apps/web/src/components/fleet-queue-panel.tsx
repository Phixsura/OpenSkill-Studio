"use client";
export function FleetQueuePanel({ totalDepth, maxDepth, queues, backlog }: { totalDepth: number; maxDepth: number; queues: number; backlog: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 Fleet Queues</h3>
    <div className="text-sm">{totalDepth.toLocaleString()} total · max {maxDepth.toLocaleString()} · {queues} queues</div>
    {backlog && <span className="text-xs text-yellow-600">⚠️ Queue backlog detected</span>}
  </div>);
}
