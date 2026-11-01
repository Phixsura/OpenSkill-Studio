"use client";

interface AnalyticsInfo { total_sent: number; total_failed: number; success_rate: number; avg_latency_ms: number; active_destinations: number; top_event_type: string; }
interface Props { analytics: AnalyticsInfo; appName: string; }

export default function APIWebhookAnalyticsCard({ analytics, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Webhook Analytics</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">{analytics.success_rate}%</p>
          <p className="text-[8px] text-gray-500">Success</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{analytics.total_sent.toLocaleString()}</p>
          <p className="text-[8px] text-gray-500">Sent</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{analytics.avg_latency_ms}ms</p>
          <p className="text-[8px] text-gray-500">Avg Latency</p>
        </div>
      </div>
      <div className="mt-2 flex justify-between text-[10px] text-gray-400">
        <span>{analytics.active_destinations} destinations</span>
        {analytics.top_event_type && <span>top: {analytics.top_event_type}</span>}
      </div>
    </div>
  );
}
