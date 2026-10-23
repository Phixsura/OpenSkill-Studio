"use client";

interface CachePerformanceCardProps { hits: number; misses: number; hitRate: number; efficiency: string; onPurge: () => void; }

export function CachePerformanceCard({ hits, misses, hitRate, efficiency, onPurge }: CachePerformanceCardProps) {
  const effColors: Record<string, string> = { excellent: "text-green-600", good: "text-blue-600", poor: "text-red-600" };
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Cache Performance</h3>
        <button onClick={onPurge} className="rounded border px-2 py-1 text-xs text-red-600 hover:bg-red-50">Purge</button>
      </div>
      <div className="mt-3 text-center">
        <p className={`text-3xl font-bold ${effColors[efficiency] || ""}`}>{hitRate}%</p>
        <p className="text-xs text-gray-400">Hit Rate — {efficiency}</p>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3 text-center">
        <div><p className="text-lg font-bold text-green-600">{hits.toLocaleString()}</p><p className="text-xs text-gray-400">Hits</p></div>
        <div><p className="text-lg font-bold text-red-600">{misses.toLocaleString()}</p><p className="text-xs text-gray-400">Misses</p></div>
      </div>
    </div>
  );
}
