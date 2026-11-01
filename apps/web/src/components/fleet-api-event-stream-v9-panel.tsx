"use client";
export function FleetApiEventStreamV9Panel({ streams, eps }: { streams: number; eps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Event Stream v9</h3>
    <div className="text-sm">{streams} streams · {eps.toLocaleString()} events/s</div>
  </div>);
}
