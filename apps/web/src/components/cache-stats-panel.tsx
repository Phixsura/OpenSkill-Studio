"use client";

interface CacheStats {
  entries: number;
  sizeBytes: number;
  hits: number;
  misses: number;
  hitRate: number;
  maxEntries: number;
  maxSizeBytes: number;
}

function formatBytes(b: number) {
  if (b < 1024) return `${b}B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)}KB`;
  return `${(b / 1048576).toFixed(1)}MB`;
}

export function CacheStatsPanel({
  stats,
  onClear,
  onInvalidate,
}: {
  stats: CacheStats;
  onClear?: () => void;
  onInvalidate?: (pattern: string) => void;
}) {
  const fillPct = stats.maxEntries > 0 ? Math.round((stats.entries / stats.maxEntries) * 100) : 0;
  const sizePct = stats.maxSizeBytes > 0 ? Math.round((stats.sizeBytes / stats.maxSizeBytes) * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚡ Cache</h2>
        <button onClick={onClear} className="text-xs bg-red-600 text-white px-3 py-1 rounded-lg">Clear All</button>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Hit Rate</span>
          <span className={`text-2xl font-bold ${stats.hitRate >= 80 ? "text-green-600" : stats.hitRate >= 50 ? "text-yellow-600" : "text-red-600"}`}>
            {stats.hitRate}%
          </span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Hits / Misses</span>
          <span className="text-lg font-bold">
            <span className="text-green-600">{stats.hits.toLocaleString()}</span>
            <span className="text-gray-400 mx-1">/</span>
            <span className="text-red-500">{stats.misses.toLocaleString()}</span>
          </span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Entries</span>
          <span className="text-lg font-bold">{stats.entries.toLocaleString()}</span>
        </div>
      </div>

      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Entries: {stats.entries}/{stats.maxEntries}</span>
            <span>{fillPct}%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${fillPct}%` }} />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Size: {formatBytes(stats.sizeBytes)}/{formatBytes(stats.maxSizeBytes)}</span>
            <span>{sizePct}%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
            <div className={`h-full rounded-full ${sizePct > 80 ? "bg-red-500" : "bg-green-500"}`}
              style={{ width: `${sizePct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}
