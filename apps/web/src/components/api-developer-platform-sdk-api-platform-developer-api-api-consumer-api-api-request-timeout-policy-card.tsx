"use client";

interface PolicyInfo { endpoint: string; method: string; timeout_ms: number; retry_on_timeout: boolean; max_retries: number; }
interface Props { policies: PolicyInfo[]; defaultTimeout: number; timeoutCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestTimeoutPolicyCard({ policies, defaultTimeout, timeoutCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Timeout Policies</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — default: {defaultTimeout}ms</p>
        </div>
        {timeoutCount > 0 && <span className="text-[10px] text-amber-600 dark:text-amber-400">⚠️ {timeoutCount} timeouts</span>}
      </div>
      {policies.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No custom timeout policies</p>
      ) : (
        <div className="space-y-1">
          {policies.map((p) => (
            <div key={`${p.method}-${p.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{p.method} {p.endpoint}</span>
              <span className="text-gray-400">{p.timeout_ms}ms{p.retry_on_timeout ? ` · ${p.max_retries}×` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
