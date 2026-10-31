"use client";

interface QuotaInfo { consumer_id: string; quota_type: string; allocated: number; used: number; remaining: number; usage_pct: number; exhausted: boolean; }
interface Props { quotas: QuotaInfo[]; exhaustedCount: number; appName: string; }

export default function APIDeveloperAPIApiQuotaAllocationCard({ quotas, exhaustedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Quota Allocation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exhaustedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{exhaustedCount} exhausted</span>}
      </div>
      {quotas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quotas</p>
      ) : (
        <div className="space-y-2">
          {quotas.map((q) => (
            <div key={`${q.consumer_id}-${q.quota_type}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{q.consumer_id}</span>
                <span className={q.exhausted ? "text-red-500 font-bold" : "text-gray-400"}>{q.used.toLocaleString()}/{q.allocated.toLocaleString()} {q.quota_type}</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${q.usage_pct >= 90 ? "bg-red-500" : q.usage_pct >= 70 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(q.usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
