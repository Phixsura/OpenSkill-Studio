"use client";

interface CheckInfo { check_id: string; endpoint: string; interval_seconds: number; last_result: string; consecutive_failures: number; enabled: boolean; }
interface Props { checks: CheckInfo[]; unhealthyCount: number; appName: string; }

const rDot: Record<string, string> = { healthy: "bg-green-500", unhealthy: "bg-red-500", timeout: "bg-orange-500", unknown: "bg-gray-400" };

export default function APIDeveloperAPIApiHealthCheckSchedulerCard({ checks, unhealthyCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏥 Health Checks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unhealthyCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{unhealthyCount} unhealthy</span>}
      </div>
      {checks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No health checks</p>
      ) : (
        <div className="space-y-1.5">
          {checks.map((c) => (
            <div key={c.check_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${rDot[c.last_result] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{c.endpoint}</span>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span>every {c.interval_seconds}s</span>
                {c.consecutive_failures > 0 && <span className="text-red-500">{c.consecutive_failures} fails</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
