"use client";

interface DashInfo { consumer_id: string; requests_today: number; success_rate: number; avg_latency_ms: number; quota_usage_pct: number; health_score: number; status: string; tier: string; }
interface Props { dashboards: DashInfo[]; degradedCount: number; appName: string; }

const statusColor: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", degraded: "text-yellow-600 dark:text-yellow-400", critical: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboardCard({ dashboards, degradedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📊 Consumer Dashboards</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {dashboards.length} consumers</p>
        </div>
        {degradedCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">⚠️ {degradedCount} degraded</span>}
      </div>
      {dashboards.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No dashboards</p>
      ) : (
        <div className="space-y-1">
          {dashboards.map((d) => (
            <div key={d.consumer_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{d.consumer_id} ({d.tier})</span>
              <span className={statusColor[d.status]}>{d.requests_today.toLocaleString()}/day · {d.success_rate}% · {d.health_score}hp</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
