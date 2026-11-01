"use client";

interface Config { webhookId: string; maxBatchSize: number; maxWaitSec: number; pendingCount: number; enabled: boolean; }
interface Props { configs: Config[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSenderCard({ configs, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Webhook Batching</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No batch configs</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.webhookId} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <code className="text-gray-700 dark:text-gray-300">{c.webhookId}</code>
                <span className={c.enabled ? "text-green-500" : "text-gray-400"}>{c.enabled ? "ON" : "OFF"}</span>
              </div>
              <div className="mt-0.5 text-[10px] text-gray-400">
                Max: {c.maxBatchSize} events · Wait: {c.maxWaitSec}s · Pending: {c.pendingCount}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
