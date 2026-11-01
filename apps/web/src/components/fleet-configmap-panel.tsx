"use client";
export function FleetConfigmapPanel({ total, oversized, stale, clean }: { total: number; oversized: number; stale: number; clean: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚙️ ConfigMaps</h3>
    {clean ? <span className="text-xs text-green-600">✅ All {total} clean</span>
     : <span className="text-xs text-yellow-600">⚠️ {oversized} oversized · {stale} stale</span>}
  </div>);
}
