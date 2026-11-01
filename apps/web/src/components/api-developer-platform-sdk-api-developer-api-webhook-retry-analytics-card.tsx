"use client";

interface AnalyticsInfo { destination: string; total_retries: number; retry_success_rate: number; waste_rate: number; exhausted_retries: number; }
interface Props { analytics: AnalyticsInfo[]; totalRetries: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiWebhookRetryAnalyticsCard({ analytics, totalRetries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔁 Retry Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalRetries.toLocaleString()} total retries</span>
      </div>
      {analytics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry data</p>
      ) : (
        <div className="space-y-1.5">
          {analytics.map((a) => (
            <div key={a.destination} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{new URL(a.destination).hostname}</span>
              <div className="flex gap-2 text-[10px]">
                <span className="text-green-600">{a.retry_success_rate}% success</span>
                {a.waste_rate > 0 && <span className="text-red-500">{a.waste_rate}% waste</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
