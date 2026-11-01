"use client";

interface Metrics { total_consumers: number; active_consumers: number; total_requests_today: number; error_rate_pct: number; avg_latency_ms: number; uptime_pct: number; active_incidents: number; }
interface Props { metrics: Metrics; overallHealth: string; degradedCount: number; appName: string; }

const healthStyle: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", degraded: "text-yellow-600 dark:text-yellow-400", critical: "text-red-600 dark:text-red-400" };
const healthEmoji: Record<string, string> = { healthy: "🟢", degraded: "🟡", critical: "🔴" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiHealthDashboardCard({ metrics, overallHealth, degradedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Health Dashboard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${healthStyle[overallHealth]}`}>{healthEmoji[overallHealth]} {overallHealth}</span>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{metrics.active_consumers}/{metrics.total_consumers}</div><div className="text-gray-400">Consumers</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{metrics.uptime_pct}%</div><div className="text-gray-400">Uptime</div></div>
        <div><div className={`font-semibold ${metrics.error_rate_pct > 5 ? "text-red-600" : "text-green-600"}`}>{metrics.error_rate_pct}%</div><div className="text-gray-400">Errors</div></div>
      </div>
    </div>
  );
}
