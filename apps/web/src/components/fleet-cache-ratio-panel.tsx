"use client";
export function FleetCacheRatioPanel({ ratioPct, hits, misses, effective }: { ratioPct: number; hits: number; misses: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Fleet Cache Hit Ratio</h3>
    <div className={`text-2xl font-bold ${effective ? "text-green-600" : "text-yellow-600"}`}>{ratioPct}%</div>
    <div className="text-xs text-gray-400">{hits.toLocaleString()} hits / {misses.toLocaleString()} misses</div>
  </div>);
}
