"use client";
export function FleetTurborepoPanel({ totalTasks, cacheHits, cacheMisses, timeSaved, hitRate }: { totalTasks: number; cacheHits: number; cacheMisses: number; timeSaved: number; hitRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Turborepo</h3>
    <div className="text-sm">{hitRate}% cache hit · {Math.round(timeSaved / 60)}min saved · {totalTasks} tasks</div>
  </div>);
}
