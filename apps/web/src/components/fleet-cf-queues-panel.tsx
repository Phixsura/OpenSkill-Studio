"use client";
export function FleetCfQueuesPanel({ queues, active, produced, consumed, backlog }: { queues: number; active: number; produced: number; consumed: number; backlog: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 CF Queues</h3>
    <div className="text-sm">{active}/{queues} active · {produced.toLocaleString()} produced · {backlog.toLocaleString()} backlog</div>
  </div>);
}
