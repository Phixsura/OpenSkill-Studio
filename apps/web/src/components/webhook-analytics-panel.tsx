"use client";

interface EventTypeStats { event_type: string; count: number; success_rate: number; avg_ms: number; }
interface WebhookAnalyticsPanelProps { total: number; successRate: number; avgMs: number; p99Ms: number; eventTypes: EventTypeStats[]; }

export function WebhookAnalyticsPanel({ total, successRate, avgMs, p99Ms, eventTypes }: WebhookAnalyticsPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Webhook Analytics</h3>
      <div className="mt-3 grid grid-cols-4 gap-3 text-center">
        <div><p className="text-lg font-bold">{total.toLocaleString()}</p><p className="text-xs text-gray-400">Deliveries</p></div>
        <div><p className={`text-lg font-bold ${successRate >= 99 ? "text-green-600" : "text-yellow-600"}`}>{successRate}%</p><p className="text-xs text-gray-400">Success</p></div>
        <div><p className="text-lg font-bold">{avgMs}ms</p><p className="text-xs text-gray-400">Avg</p></div>
        <div><p className="text-lg font-bold">{p99Ms}ms</p><p className="text-xs text-gray-400">P99</p></div>
      </div>
      {eventTypes.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-gray-500">By Event Type</p>
          <ul className="mt-1 space-y-1">
            {eventTypes.map(e => (
              <li key={e.event_type} className="flex items-center justify-between text-xs">
                <span className="font-mono">{e.event_type}</span>
                <span className="text-gray-400">{e.count} · {e.success_rate}% · {e.avg_ms}ms</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
