"use client";

interface Overview { total_consumers: number; active_24h: number; total_requests_24h: number; uptime_pct: number; error_rate_pct: number; avg_latency_ms: number; health: string; revenue: string; webhook_success: number; }
interface Props { overview: Overview; alerts: string[]; appName: string; }

const healthStyle: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", degraded: "text-yellow-600 dark:text-yellow-400", critical: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPlatformOverviewDashboardCard({ overview, alerts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏠 Platform Overview</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${healthStyle[overview.health]}`}>{overview.health}</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{overview.active_24h}/{overview.total_consumers}</div><div className="text-gray-400">Consumers</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{overview.uptime_pct}%</div><div className="text-gray-400">Uptime</div></div>
        <div><div className="font-semibold text-green-600 dark:text-green-400">{overview.revenue}</div><div className="text-gray-400">Revenue</div></div>
      </div>
      {alerts.length > 0 && (
        <div className="space-y-0.5">{alerts.map((a, i) => <div key={i} className="text-[10px] text-amber-600 dark:text-amber-400">{a}</div>)}</div>
      )}
    </div>
  );
}
