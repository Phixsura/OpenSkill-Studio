"use client";
export function FleetApiRequestPriorityV9Panel({ queues, total }: { queues: number; total: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔝 Request Priority v9</h3>
    <div className="text-sm">{queues} queues · {total.toLocaleString()} requests</div>
  </div>);
}
