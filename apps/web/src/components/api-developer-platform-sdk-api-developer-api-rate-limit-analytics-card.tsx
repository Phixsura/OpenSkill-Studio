"use client";

interface AnalyticsInfo { consumer_id: string; throttle_rate: number; peak_rps: number; total_requests: number; needs_upgrade: boolean; }
interface Props { analytics: AnalyticsInfo[]; upgradeCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalyticsCard({ analytics, upgradeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Rate Limit Analytics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {upgradeCount > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] text-orange-700">{upgradeCount} need upgrade</span>}
      </div>
      {analytics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limit data</p>
      ) : (
        <div className="space-y-1.5">
          {analytics.slice(0, 5).map((a) => (
            <div key={a.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.consumer_id}</span>
              <div className="flex gap-2 text-[10px]">
                <span className={a.throttle_rate >= 5 ? "text-red-500 font-bold" : "text-gray-400"}>{a.throttle_rate}% throttled</span>
                <span className="text-gray-400">{a.peak_rps} peak rps</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
