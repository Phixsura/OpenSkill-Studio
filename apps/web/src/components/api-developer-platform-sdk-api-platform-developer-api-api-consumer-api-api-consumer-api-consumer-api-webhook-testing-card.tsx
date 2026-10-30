"use client";

interface TestResult { id: string; eventType: string; status: number; latencyMs: number; success: boolean; testedAt: string; }
interface Props { results: TestResult[]; standardEvents: string[]; successRate: number; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookTestingCard({ results, standardEvents, successRate, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧪 Webhook Testing</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {(successRate * 100).toFixed(0)}% success</p>
      </div>
      <div className="mb-3">
        <div className="text-[10px] text-gray-400 mb-1">Available test events:</div>
        <div className="flex flex-wrap gap-1">{standardEvents.map((e) => <span key={e} className="rounded bg-blue-100 px-1.5 py-0.5 text-[9px] text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{e}</span>)}</div>
      </div>
      {results.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No tests run</p>
      ) : (
        <div className="space-y-1">
          {results.slice(0, 5).map((r) => (
            <div key={r.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <span className="text-gray-700 dark:text-gray-300">{r.eventType}</span>
              <div className="flex gap-2">
                <span className={r.success ? "text-green-500" : "text-red-500"}>{r.status}</span>
                <span className="text-gray-400">{r.latencyMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
