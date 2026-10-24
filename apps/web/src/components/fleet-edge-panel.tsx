"use client";
export function FleetEdgePanel({ total, online, offline, totalRps, allOnline }: { total: number; online: number; offline: number; totalRps: number; allOnline: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌍 Edge Computing</h3>
    <div className="text-sm">{online}/{total} online · {totalRps.toLocaleString()} rps</div>
    {!allOnline && <span className="text-xs text-red-500">⚠️ {offline} nodes offline</span>}
  </div>);
}
