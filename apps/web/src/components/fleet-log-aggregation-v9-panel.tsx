"use client";
export function FleetLogAggregationV9Panel({ collectors, eps }: { collectors: number; eps: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Log Aggregation v9</h3>
    <div className="text-sm">{collectors} collectors · {eps.toLocaleString()} events/s</div>
  </div>);
}
