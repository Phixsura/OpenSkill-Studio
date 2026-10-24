"use client";

interface CacheInfo { name: string; type: string; size_mb: number; max_size_mb: number;
  hits: number; misses: number; hit_rate: number; evictions: number; }
interface CacheStatsPanelProps { caches: CacheInfo[]; overallHitRate: number; onInvalidate: (name: string) => void; }

export function CacheStatsPanel({ caches, overallHitRate, onInvalidate }: CacheStatsPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Cache</h2>
        <span className={`text-sm font-bold ${overallHitRate >= 80 ? "text-green-600" : "text-yellow-600"}`}>
          {overallHitRate}% hit rate
        </span>
      </div>
      {caches.map(c => (
        <div key={c.name} className="rounded-lg border p-3 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-medium">{c.name}</span>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{c.type}</span>
            </div>
            <button onClick={() => onInvalidate(c.name)} className="text-xs text-red-500">Flush</button>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-full rounded-full bg-blue-500" style={{ width: `${c.hit_rate}%` }} />
          </div>
          <div className="mt-1 flex justify-between text-xs text-gray-400">
            <span>{c.hit_rate}% · {c.size_mb}/{c.max_size_mb} MB</span>
            <span>{c.evictions} evictions</span>
          </div>
        </div>
      ))}
    </div>
  );
}
