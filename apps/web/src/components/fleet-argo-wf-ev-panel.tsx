"use client";
export function FleetArgoWfEvPanel({ totalEvents, triggeredWorkflows, triggerRate }: { totalEvents: number; triggeredWorkflows: number; triggerRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Argo WF Events</h3>
    <div className="text-sm">{totalEvents} events · {triggeredWorkflows} triggered ({triggerRate}%)</div>
  </div>);
}
