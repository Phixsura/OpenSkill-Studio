"use client";

interface Props { totalEntries: number; hitCount: number; missCount: number; hitRate: number; evictionCount: number; ttlSeconds: number; maxEntries: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiAccessTokenCacheCard({ totalEntries, hitCount, missCount, hitRate, evictionCount, ttlSeconds, maxEntries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Token Cache</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · TTL: {ttlSeconds}s · Max: {maxEntries.toLocaleString()}</p>
      </div>
      <div className="mb-3 grid grid-cols-4 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalEntries}</div><div className="text-[9px] text-gray-400">Cached</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{hitCount}</div><div className="text-[9px] text-gray-400">Hits</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{missCount}</div><div className="text-[9px] text-gray-400">Misses</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${hitRate >= 80 ? "text-green-600" : hitRate >= 50 ? "text-amber-600" : "text-red-600"}`}>{hitRate}%</div><div className="text-[9px] text-gray-400">Hit Rate</div></div>
      </div>
      {evictionCount > 0 && <div className="text-[10px] text-amber-500">⚠ {evictionCount} evictions — consider increasing max entries</div>}
    </div>
  );
}
