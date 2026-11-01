"use client";

interface Breaker { webhookId: string; state: string; failures: int; successes: int; threshold: int; }
interface Props { breakers: Breaker[]; consumerId: string; appName: string; }

const stateColors: Record<string, string> = { closed: "text-green-500", open: "text-red-500", half_open: "text-amber-500" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreakerCard({ breakers, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Webhook Circuit Breakers</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {breakers.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhook circuits</p>
      ) : (
        <div className="space-y-1">
          {breakers.map((b) => (
            <div key={b.webhookId} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1.5 text-[11px] dark:bg-gray-800">
              <div>
                <code className="text-gray-700 dark:text-gray-300">{b.webhookId}</code>
                <span className="ml-1 text-[10px] text-gray-400">{b.failures}F / {b.successes}S</span>
              </div>
              <span className={`font-bold ${stateColors[b.state] ?? ""}`}>{b.state}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
