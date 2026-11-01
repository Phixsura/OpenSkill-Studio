"use client";
export function FleetBuildCachePanel({ hitRate, timeSaved, builds, effective }: { hitRate: number; timeSaved: number; builds: number; effective: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⚡ Build Cache</h3>
    <div className={`text-lg font-bold ${effective ? "text-green-600" : "text-yellow-600"}`}>{hitRate}% hit rate</div>
    <div className="text-xs text-gray-400">{Math.round(timeSaved / 60)}min saved · {builds} builds</div>
  </div>);
}
