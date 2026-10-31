"use client";
export function FleetBullmqPanel({ queues, waiting, active, completed, failed }: { queues: number; waiting: number; active: number; completed: number; failed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🐂 BullMQ</h3>
    <div className="text-sm">{queues} queues · {waiting} waiting · {active} active · {completed.toLocaleString()}/24h</div>
  </div>);
}
