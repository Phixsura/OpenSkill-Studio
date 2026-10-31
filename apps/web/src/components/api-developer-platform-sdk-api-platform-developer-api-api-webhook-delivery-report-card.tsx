"use client";

interface Metrics { total_deliveries: number; successful: number; failed: number; retried: number; avg_latency_ms: number; }
interface Props { period: string; metrics: Metrics; successRate: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReportCard({ period, metrics, successRate, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📬 Delivery Report</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {period}</p>
        </div>
        <span className={`text-sm font-bold ${successRate >= 95 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>{successRate}%</span>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{metrics.total_deliveries.toLocaleString()}</div><div className="text-gray-400">Total</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{metrics.successful.toLocaleString()}</div><div className="text-gray-400">Success</div></div>
        <div><div className="font-semibold text-red-600 dark:text-red-400">{metrics.failed}</div><div className="text-gray-400">Failed</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{metrics.avg_latency_ms}ms</div><div className="text-gray-400">Avg Latency</div></div>
      </div>
    </div>
  );
}
