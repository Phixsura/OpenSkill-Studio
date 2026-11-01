"use client";

interface EntryInfo { consumer_id: string; api_calls_used: number; api_calls_limit: number; api_usage_pct: number; any_over_limit: boolean; }
interface Props { entries: EntryInfo[]; period: string; overLimitCount: number; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiConsumerQuotaUsageReportCard({ entries, period, overLimitCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Quota Usage Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} · {period}</p>
        </div>
        {overLimitCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{overLimitCount} over limit</span>}
      </div>
      {entries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quota data</p>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <div key={e.consumer_id}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{e.consumer_id}</span>
                <span className={e.any_over_limit ? "text-red-500 font-bold" : "text-gray-400"}>{e.api_calls_used.toLocaleString()}/{e.api_calls_limit.toLocaleString()}</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${e.api_usage_pct > 100 ? "bg-red-500" : e.api_usage_pct > 80 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(e.api_usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
