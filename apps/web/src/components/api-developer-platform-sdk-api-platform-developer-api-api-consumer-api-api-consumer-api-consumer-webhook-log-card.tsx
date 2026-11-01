"use client";

interface LogEntry { id: string; eventType: string; status: number | null; success: boolean; responseTimeMs: number; attempt: number; timestamp: string; }
interface Props { logs: LogEntry[]; consumerId: string; failureRate: number; avgResponseMs: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLogCard({ logs, consumerId, failureRate, avgResponseMs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Webhook Log</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-3 grid grid-cols-2 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className={`font-bold ${failureRate > 0.1 ? "text-red-600" : "text-green-600"}`}>{(failureRate * 100).toFixed(1)}%</div>
          <div className="text-[10px] text-gray-400">Failure rate</div>
        </div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800">
          <div className="font-bold text-gray-700 dark:text-gray-300">{avgResponseMs.toFixed(0)}ms</div>
          <div className="text-[10px] text-gray-400">Avg response</div>
        </div>
      </div>
      {logs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No webhook logs</p>
      ) : (
        <div className="space-y-1">
          {logs.slice(0, 8).map((l) => (
            <div key={l.id} className="flex items-center justify-between rounded bg-gray-50 px-2 py-1 text-[10px] dark:bg-gray-800">
              <span className="text-gray-600 dark:text-gray-400">{l.eventType}</span>
              <div className="flex gap-2">
                <span className={l.success ? "text-green-500" : "text-red-500"}>{l.status ?? "ERR"}</span>
                <span className="text-gray-400">{l.responseTimeMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
