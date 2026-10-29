"use client";

interface DashInfo { total_rules: number; active_rules: number; throttled_requests: number; total_consumers: number; exhausted_consumers: number; avg_utilization_pct: number; }
interface Props { dashboard: DashInfo; appName: string; }

export default function APIDeveloperAPIRateLimitDashboardCard({ dashboard: d, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚦 Rate Limit Dashboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Rules", v: `${d.active_rules}/${d.total_rules}` },
          { l: "Throttled", v: d.throttled_requests.toLocaleString() },
          { l: "Consumers", v: d.total_consumers },
          { l: "Exhausted", v: d.exhausted_consumers },
          { l: "Utilization", v: `${d.avg_utilization_pct}%` },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
