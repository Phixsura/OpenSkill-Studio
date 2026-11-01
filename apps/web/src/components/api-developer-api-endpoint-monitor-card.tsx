"use client";

interface MonitorInfo { method: string; path: string; status: string; avg_response_ms: number; error_rate_pct: number; requests_per_minute: number; }
interface Props { monitors: MonitorInfo[]; appName: string; }

const sDot: Record<string, string> = { healthy: "bg-green-500", slow: "bg-yellow-500", erroring: "bg-orange-500", down: "bg-red-500" };

export default function APIDeveloperAPIEndpointMonitorCard({ monitors, appName }: Props) {
  const unhealthy = monitors.filter((m) => m.status !== "healthy").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📡 Endpoint Monitor</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{monitors.length} monitored</span>
          {unhealthy > 0 && <p className="text-[10px] text-red-500">{unhealthy} unhealthy</p>}
        </div>
      </div>
      {monitors.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoints monitored</p>
      ) : (
        <div className="space-y-1">
          {monitors.map((m) => (
            <div key={`${m.method}-${m.path}`} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${sDot[m.status] ?? "bg-gray-400"}`} />
                <span className="font-mono text-gray-700 dark:text-gray-300">{m.method} {m.path}</span>
              </div>
              <span className="text-gray-400">{m.avg_response_ms}ms · {m.requests_per_minute} rpm</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
