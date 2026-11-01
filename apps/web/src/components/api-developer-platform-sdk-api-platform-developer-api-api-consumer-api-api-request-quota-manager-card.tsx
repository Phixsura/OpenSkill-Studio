"use client";

interface QuotaInfo { consumer_id: string; window_type: string; limit: number; used: number; remaining: number; usage_pct: number; rollover: number; }
interface Props { quotas: QuotaInfo[]; nearLimitCount: number; appName: string; }

const barColor = (pct: number) => pct >= 95 ? "bg-red-500" : pct >= 80 ? "bg-yellow-500" : "bg-green-500";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestQuotaManagerCard({ quotas, nearLimitCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Quota Manager</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {nearLimitCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">⚠️ {nearLimitCount} near limit</span>}
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => (
            <div key={`${q.consumer_id}-${q.window_type}`} className="text-[11px]">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">{q.consumer_id} / {q.window_type}</span>
                <span className="text-gray-400">{q.used.toLocaleString()}/{(q.limit + q.rollover).toLocaleString()}</span>
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
