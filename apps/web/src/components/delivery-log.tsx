"use client";

interface Delivery { id: string; eventType: string; statusCode: number; success: boolean;
  durationMs: number; deliveredAt: string; }
interface DeliveryLogProps { deliveries: Delivery[]; successRate: number; avgDurationMs: number; }

export function DeliveryLog({ deliveries, successRate, avgDurationMs }: DeliveryLogProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Delivery Log</h3>
        <div className="flex gap-3 text-xs text-gray-400">
          <span className={successRate >= 95 ? "text-green-600" : "text-red-600"}>{successRate}%</span>
          <span>avg {avgDurationMs}ms</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700 max-h-56 overflow-y-auto">
        {deliveries.map(d => (
          <div key={d.id} className="flex items-center justify-between px-4 py-2">
            <div className="flex items-center gap-2">
              <span className={d.success ? "text-green-600" : "text-red-600"}>{d.success ? "✓" : "✗"}</span>
              <span className="text-sm font-mono">{d.eventType}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-gray-400">
              <span className="font-mono">{d.statusCode}</span>
              <span>{d.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
