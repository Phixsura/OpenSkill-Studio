"use client";

interface CacheStatsInfo {
  hits: number;
  misses: number;
  hit_rate: number;
  entries: number;
}

interface CachedEntryInfo {
  cache_key: string;
  status_code: number;
  etag: string;
  expires_in_seconds: number;
}

interface ResponseCacheCardProps {
  stats: CacheStatsInfo;
  recentEntries: CachedEntryInfo[];
  appName: string;
}

function formatNum(n: number): string {
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export default function ResponseCacheCard({
  stats,
  recentEntries,
  appName,
}: ResponseCacheCardProps) {
  const rateColor =
    stats.hit_rate >= 80
      ? "text-green-600 dark:text-green-400"
      : stats.hit_rate >= 50
        ? "text-yellow-600"
        : "text-red-600";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Response Cache</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${rateColor}`}>{stats.hit_rate}% hit rate</span>
      </div>

      <div className="mb-4 grid grid-cols-3 gap-3 text-center">
        <div>
          <p className="text-lg font-bold text-green-600 dark:text-green-400">
            {formatNum(stats.hits)}
          </p>
          <p className="text-[10px] text-gray-500">Hits</p>
        </div>
        <div>
          <p className="text-lg font-bold text-red-600 dark:text-red-400">
            {formatNum(stats.misses)}
          </p>
          <p className="text-[10px] text-gray-500">Misses</p>
        </div>
        <div>
          <p className="text-lg font-bold text-gray-800 dark:text-gray-200">{stats.entries}</p>
          <p className="text-[10px] text-gray-500">Cached</p>
        </div>
      </div>

      {recentEntries.length > 0 && (
        <div>
          <p className="mb-1.5 text-xs font-medium text-gray-500">Recent Entries</p>
          <div className="space-y-1">
            {recentEntries.map((e) => (
              <div key={e.cache_key} className="flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-gray-600 dark:text-gray-400">{e.cache_key}</span>
                  <span className={e.status_code < 400 ? "text-green-600" : "text-red-500"}>
                    {e.status_code}
                  </span>
                </div>
                <span className="text-gray-400">{e.expires_in_seconds}s TTL</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
