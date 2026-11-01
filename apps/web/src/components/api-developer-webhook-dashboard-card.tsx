"use client";

interface DashInfo { total_destinations: number; active_subscriptions: number; total_delivered: number; total_failed: number; dead_letter_count: number; circuit_breakers_open: number; avg_delivery_ms: number; success_rate: number; }
interface Props { dashboard: DashInfo; appName: string; }

export default function APIDeveloperWebhookDashboardCard({ dashboard: d, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Webhook Dashboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-4 gap-1.5 text-center">
        {[
          { l: "Destinations", v: d.total_destinations },
          { l: "Subscriptions", v: d.active_subscriptions },
          { l: "Delivered", v: d.total_delivered.toLocaleString() },
          { l: "Failed", v: d.total_failed },
          { l: "Success", v: `${d.success_rate}%` },
          { l: "Avg Latency", v: `${d.avg_delivery_ms}ms` },
          { l: "Dead Letters", v: d.dead_letter_count },
          { l: "CB Open", v: d.circuit_breakers_open },
        ].map((m) => (
          <div key={m.l} className="rounded bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-[11px] font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
