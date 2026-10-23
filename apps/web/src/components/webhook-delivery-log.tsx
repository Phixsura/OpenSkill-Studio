"use client";

interface DeliveryEntry { id: string; eventType: string; statusCode: number;
  durationMs: number; success: boolean; url: string; }
interface WebhookDeliveryLogProps { entries: DeliveryEntry[]; totalDeliveries: number;
  successRate: number; avgDurationMs: number; }

export function WebhookDeliveryLog({ entries, totalDeliveries, successRate, avgDurationMs }: WebhookDeliveryLogProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Delivery Log</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>{totalDeliveries} total</span>
          <span>{successRate}% success</span>
          <span>Avg {avgDurationMs}ms</span>
        </div>
      </div>
      <div className="max-h-64 overflow-y-auto divide-y dark:divide-gray-700">
        {entries.map(e => (
          <div key={e.id} className="flex items-center justify-between px-4 py-2 text-sm">
            <div className="flex items-center gap-2">
              <span>{e.success ? "✅" : "❌"}</span>
              <span className="font-mono text-xs">{e.eventType}</span>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span className={e.statusCode < 400 ? "text-green-600" : "text-red-500"}>{e.statusCode}</span>
              <span>{e.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
