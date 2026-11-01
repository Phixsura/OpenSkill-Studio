"use client";

interface WebhookStatsInfo {
  total_sent: number;
  total_failed: number;
  total_retried: number;
  success_rate: number;
  avg_latency: number;
  p95_latency: number;
}

interface APIWebhookStatsCardProps {
  stats: WebhookStatsInfo;
  appName: string;
}

export default function APIWebhookStatsCard({ stats, appName }: APIWebhookStatsCardProps) {
  const total = stats.total_sent + stats.total_failed;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Webhook Stats</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{total.toLocaleString()} deliveries</span>
      </div>

      <div className="mb-3 grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">{stats.success_rate}%</p>
          <p className="text-[9px] text-gray-500">success</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{stats.avg_latency}ms</p>
          <p className="text-[9px] text-gray-500">avg latency</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
          <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{stats.p95_latency}ms</p>
          <p className="text-[9px] text-gray-500">p95</p>
        </div>
      </div>

      <div className="flex justify-between text-[10px] text-gray-400">
        <span>{stats.total_sent.toLocaleString()} sent</span>
        <span>{stats.total_failed} failed</span>
        <span>{stats.total_retried} retried</span>
      </div>
    </div>
  );
}
