"use client";

interface MonitorInfo {
  monitor_id: string;
  service_name: string;
  uptime_pct: number;
  consecutive_down: number;
  total_checks: number;
}

interface APIUptimeMonitorCardProps {
  monitors: MonitorInfo[];
  appName: string;
}

export default function APIUptimeMonitorCard({ monitors, appName }: APIUptimeMonitorCardProps) {
  const down = monitors.filter((m) => m.consecutive_down > 0).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📶 Uptime Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{monitors.length} services</span>
          {down > 0 && <p className="text-[10px] text-red-500">{down} down</p>}
        </div>
      </div>

      {monitors.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No uptime monitors</p>
      ) : (
        <div className="space-y-1.5">
          {monitors.map((m) => (
            <div key={m.monitor_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${m.consecutive_down > 0 ? "bg-red-500" : "bg-green-500"}`} />
                <span className="text-xs text-gray-700 dark:text-gray-300">{m.service_name}</span>
              </div>
              <span className={`text-[11px] font-medium ${m.uptime_pct >= 99.9 ? "text-green-600" : m.uptime_pct >= 99 ? "text-yellow-600" : "text-red-500"}`}>
                {m.uptime_pct}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
