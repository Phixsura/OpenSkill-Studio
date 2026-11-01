"use client";

interface StatsInfo { requests_today: number; errors_today: number; active_developers: number; webhook_deliveries_today: number; avg_response_ms: number; uptime_today: number; }
interface Props { stats: StatsInfo; appName: string; }

export default function APIDeveloperAPIQuickStatsCard({ stats: s, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Quick Stats</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — Today</p>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        {[
          { l: "Requests", v: s.requests_today.toLocaleString() },
          { l: "Errors", v: s.errors_today },
          { l: "Developers", v: s.active_developers },
          { l: "Webhooks", v: s.webhook_deliveries_today.toLocaleString() },
          { l: "Avg Response", v: `${s.avg_response_ms}ms` },
          { l: "Uptime", v: `${s.uptime_today}%` },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
            <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[8px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
