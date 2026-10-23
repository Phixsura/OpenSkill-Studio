"use client";

interface Delivery { id: string; event: string; url: string; statusCode: number;
  success: boolean; durationMs: number; timestamp: string; }
interface WebhookLogsPageProps { deliveries: Delivery[]; total: number; page: number;
  totalPages: number; successRate: number; onPageChange: (page: number) => void; }

export function WebhookLogsPage({ deliveries, total, page, totalPages, successRate, onPageChange }: WebhookLogsPageProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📋 Webhook Logs</h2>
        <span className={`text-xs ${successRate >= 95 ? "text-green-600" : "text-red-600"}`}>{successRate}% · {total} deliveries</span>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {deliveries.map(d => (
          <div key={d.id} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={d.success ? "text-green-600" : "text-red-600"}>{d.success ? "✓" : "✗"}</span>
              <code className="text-sm font-mono">{d.event}</code>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span className="font-mono">{d.statusCode}</span>
              <span>{d.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
      <div className="flex justify-center gap-1">
        <button onClick={() => onPageChange(page - 1)} disabled={page <= 1} className="rounded border px-2 py-1 text-xs disabled:opacity-30 dark:border-gray-700">←</button>
        <span className="px-2 py-1 text-xs">{page}/{totalPages}</span>
        <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages} className="rounded border px-2 py-1 text-xs disabled:opacity-30 dark:border-gray-700">→</button>
      </div>
    </div>
  );
}
