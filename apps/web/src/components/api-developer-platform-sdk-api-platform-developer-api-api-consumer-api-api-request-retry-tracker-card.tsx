"use client";

interface RetryInfo { consumer_id: string; endpoint: string; total_attempts: number; success_rate: number; max_reached: number; }
interface Props { records: RetryInfo[]; totalRetries: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestRetryTrackerCard({ records, totalRetries, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Retry Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalRetries.toLocaleString()} total retries</p>
        </div>
      </div>
      {records.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry data</p>
      ) : (
        <div className="space-y-1">
          {records.map((r) => (
            <div key={`${r.consumer_id}-${r.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.consumer_id} → {r.endpoint}</span>
              <span className="text-gray-400">{r.total_attempts}× · {r.success_rate}% ok</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
