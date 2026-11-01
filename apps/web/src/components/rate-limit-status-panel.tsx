"use client";

interface EndpointLimit { endpoint: string; method: string; limit: number; used: number; remaining: number;
  usage_pct: number; throttled: boolean; warning: boolean; reset_in_sec: number; }
interface RateLimitStatusPanelProps { endpoints: EndpointLimit[]; overallHealth: string; }

export function RateLimitStatusPanel({ endpoints, overallHealth }: RateLimitStatusPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Rate Limits</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${overallHealth === "healthy" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {overallHealth}
        </span>
      </div>
      <div className="space-y-2">
        {endpoints.map(ep => (
          <div key={`${ep.method}-${ep.endpoint}`} className="rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs dark:bg-gray-800">{ep.method}</span>
                <span className="text-sm">{ep.endpoint}</span>
              </div>
              <span className="text-xs text-gray-400">{ep.remaining}/{ep.limit}</span>
            </div>
            <div className="mt-1.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${ep.throttled ? "bg-red-500" : ep.warning ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(ep.usage_pct, 100)}%` }} />
            </div>
            {ep.throttled && <p className="mt-1 text-xs text-red-500">Throttled — resets in {ep.reset_in_sec}s</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
