"use client";

interface Endpoint { method: string; path: string; currentRpm: number; rpmLimit: number;
  usagePct: number; throttled: boolean; }
interface RateLimitDashboardPageProps { endpoints: Endpoint[]; totalRpm: number;
  throttledCount: number; planLimit: number; healthy: boolean; }

const methodColors: Record<string, string> = {
  GET: "text-green-600", POST: "text-blue-600", PUT: "text-yellow-600", DELETE: "text-red-600",
};

export function RateLimitDashboardPage({ endpoints, totalRpm, throttledCount, planLimit, healthy }: RateLimitDashboardPageProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">⚡ Rate Limits</h2>
        <div className="flex items-center gap-2">
          <span className={`h-2.5 w-2.5 rounded-full ${healthy ? "bg-green-500" : "bg-red-500 animate-pulse"}`} />
          <span className="text-xs text-gray-400">{totalRpm} RPM / {planLimit} limit · {throttledCount} throttled</span>
        </div>
      </div>
      <div className="space-y-2">
        {endpoints.map((ep, i) => (
          <div key={i} className={`rounded-lg border px-4 py-2.5 ${ep.throttled ? "border-red-300 bg-red-50 dark:bg-red-900/10 dark:border-red-700" : "dark:border-gray-700"}`}>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className={`font-mono text-xs ${methodColors[ep.method] ?? ""}`}>{ep.method}</span>
                <code className="font-mono text-xs">{ep.path}</code>
              </div>
              <span className={`text-xs ${ep.throttled ? "text-red-600 font-bold" : "text-gray-400"}`}>
                {ep.currentRpm}/{ep.rpmLimit} ({ep.usagePct}%)
              </span>
            </div>
            <div className="mt-1 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${ep.usagePct > 80 ? "bg-red-500" : "bg-blue-500"}`}
                style={{ width: `${Math.min(ep.usagePct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
