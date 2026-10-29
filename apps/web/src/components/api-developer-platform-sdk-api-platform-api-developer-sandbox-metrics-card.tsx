"use client";

interface MetricsInfo { sandbox_id: string; total_requests: number; unique_developers: number; avg_response_ms: number; error_rate: number; health: string; active: boolean; }
interface Props { sandboxes: MetricsInfo[]; unhealthyCount: number; appName: string; }

const hDot: Record<string, string> = { healthy: "bg-green-500", degraded: "bg-yellow-500", unhealthy: "bg-red-500" };

export default function APIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetricsCard({ sandboxes, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏖️ Sandbox Metrics</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {sandboxes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No sandbox data</p>
      ) : (
        <div className="space-y-1.5">
          {sandboxes.map((s) => (
            <div key={s.sandbox_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${hDot[s.health] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{s.sandbox_id}</span>
              </div>
              <span className="text-gray-400">{s.total_requests.toLocaleString()} reqs · {s.unique_developers} devs · {s.error_rate}% err</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
