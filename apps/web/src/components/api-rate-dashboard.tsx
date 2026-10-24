"use client";

interface RateEndpoint { path: string; method: string; currentRpm: number;
  rpmLimit: number; usagePct: number; throttled: boolean; }
interface ApiRateDashboardProps { endpoints: RateEndpoint[]; totalRpm: number;
  throttledCount: number; healthy: boolean; }

export function ApiRateDashboard({ endpoints, totalRpm, throttledCount, healthy }: ApiRateDashboardProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Rate Limits</h3>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${healthy ? "bg-green-500" : "bg-red-500 animate-pulse"}`} />
          <span className="text-xs text-gray-400">{totalRpm} RPM · {throttledCount} throttled</span>
        </div>
      </div>
      <div className="space-y-1.5">
        {endpoints.map((ep, i) => (
          <div key={i} className={`rounded border px-3 py-2 dark:border-gray-700 ${ep.throttled ? "bg-red-50 dark:bg-red-900/10 border-red-200" : ""}`}>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="rounded bg-gray-100 px-1 py-0.5 text-xs font-mono dark:bg-gray-800">{ep.method}</span>
                <span className="font-mono text-xs">{ep.path}</span>
              </div>
              <span className={`text-xs ${ep.throttled ? "text-red-600 font-medium" : "text-gray-400"}`}>
                {ep.currentRpm}/{ep.rpmLimit} ({ep.usagePct}%)
              </span>
            </div>
            <div className="mt-1 h-1 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${ep.usagePct > 80 ? "bg-red-500" : "bg-blue-500"}`}
                style={{ width: `${Math.min(ep.usagePct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
