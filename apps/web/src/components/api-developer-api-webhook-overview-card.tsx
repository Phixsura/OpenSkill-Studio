"use client";

interface OverviewInfo { total_events_emitted: number; total_deliveries: number; total_destinations: number; total_subscriptions: number; success_rate: number; avg_delivery_ms: number; circuit_breakers_open: number; dead_letters: number; retry_rate: number; idempotency_dedup_count: number; active_filters: number; }
interface Props { overview: OverviewInfo; appName: string; }

export default function APIDeveloperAPIWebhookOverviewCard({ overview: o, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Webhook Overview</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Complete Webhook Platform</p>
        </div>
        <span className={`text-lg font-bold ${o.success_rate >= 99 ? "text-green-600" : o.success_rate >= 95 ? "text-yellow-600" : "text-red-500"}`}>{o.success_rate}%</span>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Events", v: o.total_events_emitted.toLocaleString() },
          { l: "Deliveries", v: o.total_deliveries.toLocaleString() },
          { l: "Destinations", v: o.total_destinations },
          { l: "Subscriptions", v: o.total_subscriptions },
          { l: "Avg Latency", v: `${o.avg_delivery_ms}ms` },
          { l: "CB Open", v: o.circuit_breakers_open },
          { l: "Dead Letters", v: o.dead_letters },
          { l: "Deduped", v: o.idempotency_dedup_count },
          { l: "Retry Rate", v: `${o.retry_rate}%` },
          { l: "Filters", v: o.active_filters },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[6px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
