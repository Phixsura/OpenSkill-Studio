"use client";

interface PlatformStatsInfo {
  total_services: number;
  total_endpoints: number;
  total_consumers: number;
  total_api_calls: number;
  total_webhooks_sent: number;
  overall_health: number;
  uptime_pct: number;
  active_incidents: number;
}

interface APIPlatformStatsCardProps {
  stats: PlatformStatsInfo;
  appName: string;
}

export default function APIPlatformStatsCard({ stats, appName }: APIPlatformStatsCardProps) {
  const healthColor = stats.overall_health >= 95 ? "text-green-600" : stats.overall_health >= 80 ? "text-yellow-600" : "text-red-500";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🌐 Platform Overview</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-2xl font-bold ${healthColor}`}>{stats.overall_health}%</span>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { label: "Services", value: stats.total_services },
          { label: "Endpoints", value: stats.total_endpoints },
          { label: "Consumers", value: stats.total_consumers },
          { label: "API Calls", value: stats.total_api_calls.toLocaleString() },
          { label: "Webhooks", value: stats.total_webhooks_sent.toLocaleString() },
          { label: "Uptime", value: `${stats.uptime_pct}%` },
          { label: "Incidents", value: stats.active_incidents },
        ].map((m) => (
          <div key={m.label} className="rounded-lg bg-gray-50 py-1.5 dark:bg-gray-800">
            <p className="text-sm font-bold text-gray-900 dark:text-gray-100">{m.value}</p>
            <p className="text-[8px] text-gray-500">{m.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
