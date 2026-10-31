"use client";

interface PolicyInfo { endpoint: string; ttl_seconds: number; cache_control: string; is_cacheable: boolean; vary_headers: string[]; }
interface Props { policies: PolicyInfo[]; cacheableCount: number; appName: string; }

const ccBadge: Record<string, string> = { public: "bg-green-100 text-green-700", private: "bg-blue-100 text-blue-700", "no-cache": "bg-yellow-100 text-yellow-700", "no-store": "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicyCard({ policies, cacheableCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💾 Caching Policies</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {cacheableCount}/{policies.length} cacheable</p>
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No caching policies</p>
      ) : (
        <div className="space-y-1.5">
          {policies.map((p) => (
            <div key={p.endpoint} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.endpoint}</span>
              <div className="flex gap-1.5">
                <span className={`rounded px-1 py-0.5 text-[9px] ${ccBadge[p.cache_control] ?? ""}`}>{p.cache_control}</span>
                <span className="text-gray-400">{p.ttl_seconds}s</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
