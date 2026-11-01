"use client";
export function FleetTaskQueueV9Panel({ queues, workers }: { queues: number; workers: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📬 Task Queue v9</h3>
    <div className="text-sm">{queues} queues · {workers} workers</div>
  </div>);
}
