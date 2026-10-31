"use client";

interface EndpointUptime { endpoint: string; uptime_pct: number; downtime_minutes: number; }
interface Props { endpoints: EndpointUptime[]; slaBreachCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiUptimeMonitorCard({ endpoints, slaBreachCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📈 Uptime Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {endpoints.length} endpoints</p>
        </div>
        {slaBreachCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {slaBreachCount} SLA breach</span>}
      </div>
      {endpoints.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No uptime data</p>
      ) : (
        <div className="space-y-1.5">
          {endpoints.map((e) => (
            <div key={e.endpoint} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{e.endpoint}</span>
                <span className={e.uptime_pct >= 99.9 ? "font-bold text-green-600 dark:text-green-400" : "font-bold text-red-600 dark:text-red-400"}>{e.uptime_pct}%</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1 rounded-full ${e.uptime_pct >= 99.9 ? "bg-green-500" : "bg-red-500"}`} style={{ width: `${e.uptime_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
