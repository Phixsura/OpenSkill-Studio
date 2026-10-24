"use client";
export function FleetEventBusV9Panel({ topics, eps }: { topics: number; eps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Event Bus v9</h3>
    <div className="text-sm">{topics} topics · {eps.toLocaleString()} events/s</div>
  </div>);
}
