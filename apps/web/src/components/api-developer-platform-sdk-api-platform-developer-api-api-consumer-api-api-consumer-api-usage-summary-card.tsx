"use client";

interface SummaryInfo { consumer_id: string; total_requests: number; success_rate: number; avg_latency_ms: number; unique_endpoints: number; data_total_mb: number; }
interface Props { summaries: SummaryInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageSummaryCard({ summaries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Consumer Usage</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {summaries.length} consumers</p>
      </div>
      {summaries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage data</p>
      ) : (
        <div className="space-y-1">
          {summaries.map((s) => (
            <div key={s.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.consumer_id}</span>
              <span className="text-gray-400">{s.total_requests.toLocaleString()} reqs · {s.success_rate}% · {s.avg_latency_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
