"use client";
export function FleetClearmlPanel({ servers, running, tasks, workers }: { servers: number; running: number; tasks: number; workers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 ClearML</h3>
    <div className="text-sm">{running}/{servers} running · {tasks.toLocaleString()} tasks · {workers} workers</div>
  </div>);
}
