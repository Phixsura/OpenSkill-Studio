"use client";

interface Config { webhookId: string; maxPerSec: number; maxPerMin: number; maxPerHour: number; burst: number; currentSec: number; currentMin: number; }
interface Props { configs: Config[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiterCard({ configs, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Webhook Rate Limiter</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rate limits configured</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => {
            const secPct = c.maxPerSec > 0 ? Math.round((c.currentSec / c.maxPerSec) * 100) : 0;
            return (
              <div key={c.webhookId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
                <div className="flex items-center justify-between text-[11px]">
                  <code className="text-gray-700 dark:text-gray-300">{c.webhookId}</code>
                  <span className="text-[10px] text-gray-400">{c.maxPerSec}/s · {c.maxPerMin}/m{c.burst > 0 ? ` +${c.burst} burst` : ""}</span>
                </div>
                <div className="mt-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={`h-full rounded-full ${secPct >= 90 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${Math.min(secPct, 100)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
