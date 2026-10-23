"use client";

interface CacheStatsCardProps { size: number; maxSize: number; hits: number;
  misses: number; hitRateDisplay: string; onFlush: () => void; }

export function CacheStatsCard({ size, maxSize, hits, misses, hitRateDisplay, onFlush }: CacheStatsCardProps) {
  const fillPct = Math.round((size / Math.max(maxSize, 1)) * 100);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💾 Response Cache</h3>
        <span className="text-sm font-bold">{hitRateDisplay} hit rate</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{size}</p><p className="text-xs text-gray-400">Entries</p></div>
        <div><p className="text-lg font-bold">{maxSize}</p><p className="text-xs text-gray-400">Max</p></div>
        <div><p className="text-lg font-bold text-green-600">{hits}</p><p className="text-xs text-gray-400">Hits</p></div>
        <div><p className="text-lg font-bold text-red-500">{misses}</p><p className="text-xs text-gray-400">Misses</p></div>
      </div>
      <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-3">
        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${fillPct}%` }} />
      </div>
      <button onClick={onFlush}
        className="w-full py-1.5 text-xs border border-red-200 text-red-600 rounded hover:bg-red-50">Flush Cache</button>
    </div>
  );
}
