"use client";

interface MetricsInfo { consumer_id: string; success_rate: number; avg_latency_ms: number; retry_rate: number; total_deliveries: number; }
interface Props { metrics: MetricsInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetricsCard({ metrics, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Delivery Metrics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {metrics.length} consumers</p>
      </div>
      {metrics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery metrics</p>
      ) : (
        <div className="space-y-1">
          {metrics.map((m) => (
            <div key={m.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{m.consumer_id}</span>
              <span className="text-gray-400">{m.success_rate}% · {m.avg_latency_ms}ms · {m.total_deliveries.toLocaleString()} del</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
