"use client";

interface Entry { key: string; status: number; createdAt: string; expiresAt: string; }
interface Props { entries: Entry[]; ttlHours: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestDeduplicationCard({ entries, ttlHours, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔑 Request Deduplication</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — TTL: {ttlHours}h · {entries.length} cached</p>
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No cached idempotency keys</p>
      ) : (
        <div className="space-y-1">
          {entries.slice(0, 10).map((e) => (
            <div key={e.key} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <code className="truncate text-gray-600 dark:text-gray-400">{e.key}</code>
              <div className="flex gap-2">
                <span className={`font-medium ${e.status < 400 ? "text-green-600" : "text-red-500"}`}>{e.status}</span>
                <span className="text-gray-400">{e.expiresAt}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
