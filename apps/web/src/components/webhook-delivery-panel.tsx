"use client";

interface DeliveryEntry { webhookId: string; url: string; statusCode: number; attempt: number; success: boolean; }
interface WebhookDeliveryPanelProps { total: number; successRate: number;
  failures: number; entries: DeliveryEntry[]; }

export function WebhookDeliveryPanel({ total, successRate, failures, entries }: WebhookDeliveryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🪝 Webhook Delivery</h3>
        <span className={`text-xs ${failures > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {successRate}% success · {total} total
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={`${e.webhookId}-${e.attempt}`} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="font-mono truncate max-w-[200px]">{e.url}</div>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">#{e.attempt}</span>
              <span className={e.success ? "text-green-600" : "text-red-500"}>{e.statusCode}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
