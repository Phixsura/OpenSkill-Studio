"use client";
interface Delivery { webhookId: string; url: string; statusCode: number; durationMs: number; success: boolean; }
interface WhDeliveryLogPanelProps { deliveries: Delivery[]; failureRate: number; total: number; }
export function WhDeliveryLogPanel({ deliveries, failureRate, total }: WhDeliveryLogPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Delivery Log</h3>
        <span className={`text-xs ${failureRate > 5 ? "text-red-500" : "text-green-600"}`}>
          {failureRate}% failure · {total} total
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {deliveries.map((d, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono truncate max-w-[180px]">{d.url}</span>
            <div className="flex gap-2 text-gray-400">
              <span className={d.success ? "text-green-600" : "text-red-500"}>{d.statusCode}</span>
              <span>{d.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
