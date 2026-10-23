"use client";

interface Delivery { attempt: number; statusCode: number; success: boolean; responseMs: number; error: string; }
interface WebhookRetryViewProps { deliveries: Delivery[]; status: string; totalAttempts: number; }

export function WebhookRetryView({ deliveries, status, totalAttempts }: WebhookRetryViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Delivery Attempts</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${status === "delivered" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {status} ({totalAttempts} attempts)
        </span>
      </div>
      <div className="space-y-1">
        {deliveries.map(d => (
          <div key={d.attempt} className={`flex items-center justify-between rounded-lg border px-4 py-2 ${d.success ? "dark:border-gray-700" : "border-red-200 dark:border-red-800"}`}>
            <div className="flex items-center gap-2">
              <span className={d.success ? "text-green-600" : "text-red-600"}>{d.success ? "✓" : "✗"}</span>
              <span className="text-sm">Attempt {d.attempt}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span className="font-mono">{d.statusCode}</span>
              <span>{d.responseMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
