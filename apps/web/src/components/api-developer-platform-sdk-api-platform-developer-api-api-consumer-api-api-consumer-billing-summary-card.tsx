"use client";

interface SummaryInfo { consumer_id: string; period: string; total_dollars: string; tier: string; total_requests: number; }
interface Props { summaries: SummaryInfo[]; totalRevenue: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummaryCard({ summaries, totalRevenue, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💵 Billing Summary</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-green-600 dark:text-green-400">{totalRevenue}</span>
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No billing data</p>
      ) : (
        <div className="space-y-1">
          {summaries.map((s) => (
            <div key={`${s.consumer_id}-${s.period}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id} ({s.tier})</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">{s.total_dollars}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
