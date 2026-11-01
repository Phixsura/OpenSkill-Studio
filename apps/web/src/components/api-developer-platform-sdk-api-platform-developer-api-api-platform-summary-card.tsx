"use client";

interface Summary { total_consumers: number; active_consumers: number; total_requests_24h: number; error_rate_24h: number; uptime_30d: number; active_incidents: number; doc_coverage_pct: number; health_status: string; }
interface Props { summary: Summary; issues: string[]; appName: string; }

const healthStyle: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", degraded: "text-yellow-600 dark:text-yellow-400", critical: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlatformSummaryCard({ summary, issues, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏠 Platform Summary</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`text-sm font-bold ${healthStyle[summary.health_status]}`}>{summary.health_status}</span>
      </div>
      <div className="mb-3 grid grid-cols-3 gap-2 text-center text-[11px]">
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{summary.active_consumers}/{summary.total_consumers}</div><div className="text-gray-400">Consumers</div></div>
        <div><div className="font-semibold text-gray-900 dark:text-gray-100">{summary.uptime_30d}%</div><div className="text-gray-400">Uptime</div></div>
        <div><div className={`font-semibold ${summary.error_rate_24h > 5 ? "text-red-600" : "text-green-600"}`}>{summary.error_rate_24h}%</div><div className="text-gray-400">Errors</div></div>
      </div>
      {issues.length > 0 && (
        <div className="space-y-0.5">
          {issues.map((i, idx) => <div key={idx} className="text-[10px] text-amber-600 dark:text-amber-400">⚠️ {i}</div>)}
        </div>
      )}
    </div>
  );
}
