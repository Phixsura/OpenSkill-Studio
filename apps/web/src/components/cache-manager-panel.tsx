"use client";

interface CacheStats {
  hits: number;
  misses: number;
  hitRate: number;
  l1Size: number;
  l2Size: number;
  l1Hits: number;
  l2Hits: number;
}

export function CacheManagerPanel({
  stats,
  onClear,
  onLookup,
}: {
  stats: CacheStats;
  onClear?: () => void;
  onLookup?: (key: string) => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💾 Cache Manager</h2>
        <button onClick={onClear} className="text-xs bg-red-600 text-white px-2 py-1 rounded">Clear All</button>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Hit Rate</span>
          <span className={`text-2xl font-bold ${stats.hitRate >= 80 ? "text-green-600" : stats.hitRate >= 50 ? "text-yellow-600" : "text-red-600"}`}>{stats.hitRate}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">L1 Cache</span>
          <span className="text-lg font-bold">{stats.l1Size}</span>
          <span className="text-xs text-blue-600 block">{stats.l1Hits} hits</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">L2 Cache</span>
          <span className="text-lg font-bold">{stats.l2Size}</span>
          <span className="text-xs text-green-600 block">{stats.l2Hits} hits</span>
        </div>
      </div>

      <div className="flex gap-3 text-sm text-gray-500">
        <span className="text-green-600">✓ {stats.hits} hits</span>
        <span className="text-red-500">✗ {stats.misses} misses</span>
      </div>
    </div>
  );
}
