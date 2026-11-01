"use client";

interface Quota { consumer_id: string; resource: string; limit: number; used: number; usage_pct: number; }
interface Props { quotas: Quota[]; nearLimitCount: number; appName: string; }

const barColor = (pct: number) => pct >= 90 ? "bg-red-500" : pct >= 70 ? "bg-yellow-500" : "bg-green-500";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerQuotaAllocationCard({ quotas, nearLimitCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Quota Allocation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {quotas.length} quotas</p>
        </div>
        {nearLimitCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">⚠️ {nearLimitCount} near limit</span>}
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas allocated</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => (
            <div key={`${q.consumer_id}-${q.resource}`} className="text-[11px]">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">{q.consumer_id} / {q.resource}</span>
                <span className="text-gray-400">{q.used.toLocaleString()} / {q.limit.toLocaleString()}</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1 rounded-full ${barColor(q.usage_pct)}`} style={{ width: `${Math.min(q.usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
