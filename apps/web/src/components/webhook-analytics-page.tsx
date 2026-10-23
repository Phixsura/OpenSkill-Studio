"use client";

interface EventStats { event: string; total: number; success: number; failed: number;
  successRate: number; avgLatencyMs: number; }
interface WebhookAnalyticsPageProps { events: EventStats[]; totalDeliveries: number;
  overallSuccessRate: number; period: string; }

export function WebhookAnalyticsPage({ events, totalDeliveries, overallSuccessRate, period }: WebhookAnalyticsPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📊 Webhook Analytics</h2>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>{totalDeliveries} deliveries</span>
          <span className={overallSuccessRate >= 95 ? "text-green-600" : "text-red-600"}>{overallSuccessRate}%</span>
          <span>{period}</span>
        </div>
      </div>
      <div className="divide-y rounded-xl border dark:divide-gray-700 dark:border-gray-700">
        {events.map(e => (
          <div key={e.event} className="flex items-center justify-between px-4 py-3">
            <div>
              <code className="text-sm font-mono">{e.event}</code>
              <p className="text-xs text-gray-400 mt-0.5">{e.total} deliveries · avg {e.avgLatencyMs}ms</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-green-600">{e.success}✓</span>
              {e.failed > 0 && <span className="text-red-600">{e.failed}✗</span>}
              <span className={e.successRate >= 95 ? "text-green-600" : "text-yellow-600"}>{e.successRate}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
