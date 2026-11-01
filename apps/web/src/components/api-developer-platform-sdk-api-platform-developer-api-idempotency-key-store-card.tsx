"use client";

interface StoreInfo { total_keys: number; oldest_key_age_hours: number; hit_rate_pct: number; }
interface RecentKey { key: string; method: string; path: string; status: number; }
interface Props { info: StoreInfo; recent: RecentKey[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiIdempotencyKeyStoreCard({ info, recent, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Idempotency Keys</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{info.hit_rate_pct}% hit rate</span>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{info.total_keys.toLocaleString()}</div><div className="text-gray-400">Active Keys</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{info.oldest_key_age_hours}h</div><div className="text-gray-400">Oldest Key</div></div>
      </div>
      {recent.length > 0 && (
        <div className="space-y-1">
          {recent.map((r) => (
            <div key={r.key} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-500">{r.method}</span>
                <span className="text-gray-700 dark:text-gray-300">{r.path}</span>
              </div>
              <span className={r.status < 400 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{r.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
