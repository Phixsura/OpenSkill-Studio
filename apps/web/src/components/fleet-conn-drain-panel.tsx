"use client";
export function FleetConnDrainPanel({ total, draining, avgDrainSec, allDrained }: { total: number; draining: number; avgDrainSec: number; allDrained: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔌 Connection Draining</h3>
    {allDrained ? <span className="text-xs text-green-600">✅ All connections drained</span>
     : <span className="text-xs text-blue-500">🔄 {draining} draining (avg {avgDrainSec}s)</span>}
  </div>);
}
