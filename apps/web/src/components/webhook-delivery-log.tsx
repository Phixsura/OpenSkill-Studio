"use client";

interface Delivery { endpoint: string; event: string; statusCode: number;
  responseMs: number; success: boolean; }
interface WebhookDeliveryLogProps { deliveries: Delivery[]; successRate: number; avgResponseMs: number; }

export function WebhookDeliveryLog({ deliveries, successRate, avgResponseMs }: WebhookDeliveryLogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📬 Webhook Deliveries</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{successRate}% success</span>
          <span>avg {avgResponseMs}ms</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {deliveries.map((d, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${d.success ? "bg-green-500" : "bg-red-500"}`} />
              <span className="font-mono">{d.event}</span>
            </div>
            <div className="flex gap-3 text-gray-400">
              <span className={d.success ? "" : "text-red-500 font-medium"}>{d.statusCode}</span>
              <span>{d.responseMs}ms</span>
              <span className="truncate max-w-[120px]">{d.endpoint}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
