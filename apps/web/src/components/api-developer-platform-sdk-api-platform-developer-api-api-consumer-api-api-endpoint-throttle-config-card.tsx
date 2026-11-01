"use client";

interface ConfigInfo { endpoint: string; method: string; max_rps: number; burst_size: number; throttle_action: string; throttle_rate: number; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointThrottleConfigCard({ configs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Throttle Config</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {configs.length} endpoints</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No throttle configs</p>
      ) : (
        <div className="space-y-1">
          {configs.map((c) => (
            <div key={`${c.method}-${c.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{c.method} {c.endpoint}</span>
              <span className="text-gray-400">{c.max_rps} rps · {c.throttle_action} · {c.throttle_rate}% throttled</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
