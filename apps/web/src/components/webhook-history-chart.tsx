"use client";

interface WebhookHistoryChartProps { period: string; total: number; success: number;
  failed: number; successRate: number; avgDurationMs: number;
  byEvent: Record<string, number>; topEvent: string | null; }

export function WebhookHistoryChart({ period, total, success, failed, successRate,
  avgDurationMs, byEvent, topEvent }: WebhookHistoryChartProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Webhook History</h3>
        <span className="text-xs text-gray-400">{period} · {total} deliveries</span>
      </div>
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold text-green-600">{success}</p><p className="text-xs text-gray-400">Success</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold text-red-600">{failed}</p><p className="text-xs text-gray-400">Failed</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{successRate}%</p><p className="text-xs text-gray-400">Rate</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-lg font-bold">{avgDurationMs}ms</p><p className="text-xs text-gray-400">Avg</p>
        </div>
      </div>
      {topEvent && <p className="text-xs text-gray-400">Top event: <strong>{topEvent}</strong> ({byEvent[topEvent]})</p>}
    </div>
  );
}
