"use client";

interface Delivery {
  id: string; event: string; url: string; status_code: number;
  success: boolean; duration_ms: number; timestamp: string; attempt: number;
}
interface WebhookLogProps { deliveries: Delivery[]; successRate: number; }

export function WebhookLog({ deliveries, successRate }: WebhookLogProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Webhook Deliveries</h3>
        <span className={`text-xs font-medium ${successRate >= 90 ? "text-green-600" : "text-red-600"}`}>{successRate}% success</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {deliveries.map(d => (
          <div key={d.id} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-3">
              <span className={`h-2 w-2 rounded-full ${d.success ? "bg-green-500" : "bg-red-500"}`} />
              <div>
                <p className="text-sm font-mono">{d.event}</p>
                <p className="text-xs text-gray-400 truncate max-w-[200px]">{d.url}</p>
              </div>
            </div>
            <div className="text-right">
              <span className={`text-xs font-mono ${d.success ? "text-green-600" : "text-red-600"}`}>{d.status_code}</span>
              <p className="text-xs text-gray-400">{d.duration_ms}ms</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
