"use client";

interface CacheStatsCardProps { entries: number; totalHits: number; hitRate: number; onClear: () => void; }

export function CacheStatsCard({ entries, totalHits, hitRate, onClear }: CacheStatsCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Cache</h3>
        <button onClick={onClear} className="rounded border px-2 py-1 text-xs text-red-600 hover:bg-red-50 dark:border-gray-600">Clear</button>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-4 text-center">
        <div><p className="text-xl font-bold">{entries}</p><p className="text-xs text-gray-400">Entries</p></div>
        <div><p className="text-xl font-bold">{totalHits.toLocaleString()}</p><p className="text-xs text-gray-400">Hits</p></div>
        <div><p className="text-xl font-bold">{hitRate}%</p><p className="text-xs text-gray-400">Hit Rate</p></div>
      </div>
    </div>
  );
}
