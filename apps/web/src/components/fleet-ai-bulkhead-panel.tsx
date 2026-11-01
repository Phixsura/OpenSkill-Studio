"use client";
export function FleetAiBulkheadPanel({ bulkheads, active, partitions, rejections, isolation }: { bulkheads: number; active: number; partitions: number; rejections: number; isolation: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 AI Bulkhead</h3>
    <div className="text-sm">{active}/{bulkheads} active · {partitions} partitions · {rejections} rejections · {isolation}% isolated</div>
  </div>);
}
