"use client";

interface WebhookDeliverySummaryProps {
  total: number;
  delivered: number;
  failed: number;
  retrying: number;
  pending: number;
  successRate: number;
  avgDurationMs: number;
}

export function WebhookDeliverySummary({ total, delivered, failed, retrying, pending, successRate, avgDurationMs }: WebhookDeliverySummaryProps) {
  if (total === 0) {
    return <p className="py-3 text-center text-sm text-gray-400">No webhook deliveries yet</p>;
  }

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="mb-3 font-semibold">🔔 Webhook Deliveries</h4>
      <div className="grid grid-cols-3 gap-3 text-center text-sm">
        <div><p className="text-xl font-bold text-green-600">{delivered}</p><p className="text-xs text-gray-500">Delivered</p></div>
        <div><p className="text-xl font-bold text-red-600">{failed}</p><p className="text-xs text-gray-500">Failed</p></div>
        <div><p className="text-xl font-bold text-blue-600">{retrying + pending}</p><p className="text-xs text-gray-500">In Progress</p></div>
      </div>
      <div className="mt-3 flex justify-between text-xs text-gray-500">
        <span>Success: {successRate}%</span>
        <span>Avg: {avgDurationMs}ms</span>
        <span>Total: {total}</span>
      </div>
    </div>
  );
}
