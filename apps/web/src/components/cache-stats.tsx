"use client";

interface CacheStatsProps { size: number; maxSize: number; hits: number; misses: number;
  hitRate: number; ttlS: number; onClear: () => void; }

export function CacheStats({ size, maxSize, hits, misses, hitRate, ttlS, onClear }: CacheStatsProps) {
  const usagePct = Math.round((size / Math.max(maxSize, 1)) * 100);
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Cache</h3>
        <button onClick={onClear} className="text-xs text-red-600 hover:underline">Clear</button>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{hitRate}%</p>
          <p className="text-xs text-gray-400">Hit Rate</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{size}/{maxSize}</p>
          <p className="text-xs text-gray-400">Usage</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{ttlS}s</p>
          <p className="text-xs text-gray-400">TTL</p>
        </div>
      </div>
      <div className="flex gap-4 text-xs text-gray-400">
        <span className="text-green-600">{hits} hits</span>
        <span className="text-red-600">{misses} misses</span>
      </div>
    </div>
  );
}
