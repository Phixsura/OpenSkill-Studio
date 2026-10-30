"use client";

interface CacheInfo { path: string; ttlSec: number; entries: number; hits: number; varyBy: string[]; }
interface Props { caches: CacheInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseCacheCard({ caches, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Response Cache</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {caches.length} endpoints cached</p>
      </div>
      {caches.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No caches configured</p>
      ) : (
        <div className="space-y-2">
          {caches.map((c) => (
            <div key={c.path} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{c.path}</code>
                <span className="text-[10px] text-gray-400">TTL: {c.ttlSec}s</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>{c.entries} entries</span>
                <span>{c.hits} hits</span>
                {c.varyBy.length > 0 && <span>Vary: {c.varyBy.join(", ")}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
