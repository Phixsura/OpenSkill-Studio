"use client";

interface CacheStats { cached_entries: number; total_hits: number; }
interface InvalidationInfo { event_id: string; pattern: string; reason: string; invalidated_count: number; }
interface Props { stats: CacheStats; recentInvalidations: InvalidationInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointCacheInvalidatorCard({ stats, recentInvalidations, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗑️ Cache Invalidator</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.cached_entries}</div><div className="text-gray-400">Cached</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{stats.total_hits.toLocaleString()}</div><div className="text-gray-400">Hits</div></div>
      </div>
      {recentInvalidations.length > 0 && (
        <div className="space-y-1">
          <p className="text-[10px] font-medium text-gray-500">Recent Invalidations</p>
          {recentInvalidations.map((i) => (
            <div key={i.event_id} className="flex items-center justify-between text-[11px]">
              <span className="font-mono text-gray-700 dark:text-gray-300">{i.pattern}</span>
              <span className="text-gray-400">{i.invalidated_count} cleared</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
