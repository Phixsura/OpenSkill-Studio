"use client";

interface LimitInfo { endpoint: string; method: string; max_kb: number; rejection_rate: number; rejected_count: number; }
interface Props { limits: LimitInfo[]; defaultMaxKb: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestBodySizeLimitCard({ limits, defaultMaxKb, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📏 Body Size Limits</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — default: {defaultMaxKb}KB</p>
        </div>
      </div>
      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom limits</p>
      ) : (
        <div className="space-y-1">
          {limits.map((l) => (
            <div key={`${l.method}-${l.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{l.method} {l.endpoint}</span>
              <span className="text-gray-400">{l.max_kb}KB · {l.rejection_rate}% rejected</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
