"use client";

interface MetricsInfo { period: string; total_deliveries: number; success_rate: number; retry_rate: number; avg_latency_ms: number; }
interface Props { metrics: MetricsInfo[]; appName: string; }

export default function APIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregatorCard({ metrics, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Delivery Metrics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {metrics.length} periods</p>
      </div>
      {metrics.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No delivery metrics</p>
      ) : (
        <div className="space-y-2">
          {metrics.map((m) => (
            <div key={m.period} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{m.period}</span>
                <span className={m.success_rate >= 99 ? "text-green-600" : "text-red-500"}>{m.success_rate}%</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>{m.total_deliveries.toLocaleString()} total</span>
                <span>{m.avg_latency_ms}ms avg</span>
                <span>{m.retry_rate}% retried</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
