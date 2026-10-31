"use client";

interface Props { consumerId: string; totalRequests: number; throttledCount: number; throttleRate: number; peakHour: number; mostThrottledEndpoint: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalyticsCard({ consumerId, totalRequests, throttledCount, throttleRate, peakHour, mostThrottledEndpoint, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Rate Limit Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{totalRequests.toLocaleString()}</div><div className="text-[9px] text-gray-400">Requests</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{throttledCount}</div><div className="text-[9px] text-gray-400">Throttled</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className={`font-bold ${throttleRate > 5 ? "text-red-600" : "text-green-600"}`}>{throttleRate}%</div><div className="text-[9px] text-gray-400">Rate</div></div>
      </div>
      <div className="space-y-1 text-[10px] text-gray-500">
        <div className="flex justify-between"><span>Peak hour:</span><span className="text-gray-700 dark:text-gray-300">{peakHour}:00</span></div>
        {mostThrottledEndpoint && <div className="flex justify-between"><span>Most throttled:</span><code className="text-red-500">{mostThrottledEndpoint}</code></div>}
      </div>
    </div>
  );
}
