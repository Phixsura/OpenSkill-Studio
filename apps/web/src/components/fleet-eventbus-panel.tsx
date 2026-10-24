"use client";
export function FleetEventbusPanel({ totalEps, maxLag, topics, lagging }: { totalEps: number; maxLag: number; topics: number; lagging: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 Fleet Event Bus</h3>
    <div className="text-sm">{totalEps.toLocaleString()} eps · {maxLag.toLocaleString()}ms max lag · {topics} topics</div>
    {lagging && <span className="text-xs text-yellow-600">⚠️ Consumer lag detected</span>}
  </div>);
}
