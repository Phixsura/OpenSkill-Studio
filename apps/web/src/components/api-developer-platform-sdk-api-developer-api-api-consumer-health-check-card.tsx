"use client";

interface CheckInfo { consumer_id: string; overall_health: string; issue_count: number; error_rate_pct: number; auth_healthy: boolean; api_calls_healthy: boolean; webhook_healthy: boolean; }
interface Props { checks: CheckInfo[]; criticalCount: number; unhealthyCount: number; appName: string; }

const hColor: Record<string, string> = { healthy: "text-green-600", degraded: "text-yellow-600", critical: "text-red-600", inactive: "text-gray-400" };
const hDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", critical: "bg-red-500", inactive: "bg-gray-300" };

export default function APIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheckCard({ checks, criticalCount, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Consumer Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex gap-1">
          {criticalCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{criticalCount} critical</span>}
          {unhealthyCount > 0 && <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-[10px] text-yellow-700">{unhealthyCount} degraded</span>}
        </div>
      </div>
      {checks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumer checks</p>
      ) : (
        <div className="space-y-1">
          {checks.slice(0, 5).map((c) => (
            <div key={c.consumer_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${hDot[c.overall_health] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
              </div>
              <span className={hColor[c.overall_health] ?? ""}>{c.overall_health}{c.issue_count > 0 ? ` · ${c.issue_count} issues` : ""}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
