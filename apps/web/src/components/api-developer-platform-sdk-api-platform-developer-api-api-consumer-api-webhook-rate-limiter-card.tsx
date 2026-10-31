"use client";

interface LimitInfo { consumer_id: string; max_per_second: number; max_per_minute: number; total_limited: number; }
interface Props { limits: LimitInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiterCard({ limits, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Webhook Rate Limiter</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {limits.length} consumers</p>
      </div>
      {limits.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limits</p>
      ) : (
        <div className="space-y-1">
          {limits.map((l) => (
            <div key={l.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{l.consumer_id}</span>
              <span className="text-gray-400">{l.max_per_second}/s · {l.max_per_minute}/min · {l.total_limited} blocked</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
