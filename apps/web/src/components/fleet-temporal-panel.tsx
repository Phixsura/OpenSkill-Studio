"use client";
export function FleetTemporalPanel({ namespaces, healthy, runningWorkflows, completed }: { namespaces: number; healthy: number; runningWorkflows: number; completed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏰ Temporal</h3>
    <div className="text-sm">{healthy}/{namespaces} healthy · {runningWorkflows} running · {completed.toLocaleString()}/24h</div>
  </div>);
}
