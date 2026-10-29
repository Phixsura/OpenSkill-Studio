"use client";

interface ThrottleInfo { consumer_id: string; active: number; max_concurrent: number; throttle_rate: number; total_throttled: number; }
interface Props { consumers: ThrottleInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiRequestThrottleCard({ consumers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Request Throttle</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumers.length} consumers</p>
      </div>
      {consumers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No throttle configs</p>
      ) : (
        <div className="space-y-1.5">
          {consumers.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
                <span className="text-gray-400">{c.active}/{c.max_concurrent} active</span>
              </div>
              <div className="mt-0.5 flex justify-between text-[10px] text-gray-400">
                <span>{c.throttle_rate}% throttled</span>
                <span>{c.total_throttled} blocked</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
