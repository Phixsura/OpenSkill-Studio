"use client";
export function FleetNodeCondPanel({ total, notReady, pressure, allHealthy }: { total: number; notReady: number; pressure: number; allHealthy: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🖥️ Node Conditions</h3>
    {allHealthy ? <span className="text-xs text-green-600">✅ All {total} nodes healthy</span>
     : <span className="text-xs text-yellow-600">⚠️ {notReady} not ready · {pressure} under pressure</span>}
  </div>);
}
