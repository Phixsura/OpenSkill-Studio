"use client";

interface Delivery { delivery_id: string; event: string; url: string; status_code: number;
  response_time_ms: number; success: boolean; timestamp: string; }
interface WebhookDeliveryLogProps { deliveries: Delivery[]; successRate: number; }

export function WebhookDeliveryLog({ deliveries, successRate }: WebhookDeliveryLogProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Webhook Deliveries</h2>
        <span className={`text-sm font-medium ${successRate >= 95 ? "text-green-600" : successRate >= 80 ? "text-yellow-600" : "text-red-600"}`}>
          {successRate}% success
        </span>
      </div>
      <div className="space-y-1">
        {deliveries.map(d => (
          <div key={d.delivery_id} className="flex items-center gap-2 rounded border px-3 py-2 font-mono text-xs dark:border-gray-700">
            <span className={d.success ? "text-green-500" : "text-red-500"}>{d.success ? "✓" : "✗"}</span>
            <span className={`w-10 text-center font-bold ${d.success ? "text-green-600" : "text-red-600"}`}>{d.status_code}</span>
            <span className="flex-1 truncate text-blue-500">{d.event}</span>
            <span className="text-gray-400">{d.response_time_ms}ms</span>
            <span className="text-gray-300">{new Date(d.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
