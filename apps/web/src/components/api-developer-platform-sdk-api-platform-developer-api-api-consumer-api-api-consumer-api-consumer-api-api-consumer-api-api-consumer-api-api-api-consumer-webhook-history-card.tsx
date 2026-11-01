"use client";

interface Delivery { id: string; eventType: string; status: number | null; success: boolean; latencyMs: number; timestamp: string; }
interface Props { deliveries: Delivery[]; summary: { total: number; successful: number; failed: number; avgMs: number; successRate: number }; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistoryCard({ deliveries, summary, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📜 Webhook History</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      <div className="mb-3 grid grid-cols-4 gap-2 text-center text-[11px]">
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{summary.total}</div><div className="text-[9px] text-gray-400">Total</div></div>
        <div className="rounded bg-green-50 p-1.5 dark:bg-green-900/20"><div className="font-bold text-green-600">{summary.successful}</div><div className="text-[9px] text-gray-400">OK</div></div>
        <div className="rounded bg-red-50 p-1.5 dark:bg-red-900/20"><div className="font-bold text-red-600">{summary.failed}</div><div className="text-[9px] text-gray-400">Failed</div></div>
        <div className="rounded bg-gray-50 p-1.5 dark:bg-gray-800"><div className="font-bold text-gray-700 dark:text-gray-300">{summary.successRate}%</div><div className="text-[9px] text-gray-400">Rate</div></div>
      </div>
      {deliveries.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deliveries</p>
      ) : (
        <div className="space-y-0.5">
          {deliveries.slice(0, 6).map((d) => (
            <div key={d.id} className="flex items-center justify-between text-[10px]">
              <span className="text-gray-600 dark:text-gray-400">{d.eventType}</span>
              <div className="flex gap-2">
                <span className={d.success ? "text-green-500" : "text-red-500"}>{d.status ?? "ERR"}</span>
                <span className="text-gray-400">{d.latencyMs}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
