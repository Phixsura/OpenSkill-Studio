"use client";

interface ThrottledEndpoint { path: string; blocked: number; limit: number; currentRps: number; }
interface ThrottleDashboardProps { totalEndpoints: number; healthy: number;
  throttledCount: number; totalBlocked: number; status: string;
  throttledEndpoints: ThrottledEndpoint[]; }

export function ThrottleDashboard({ totalEndpoints, healthy, throttledCount, totalBlocked, status, throttledEndpoints }: ThrottleDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚦 Throttle Dashboard</h3>
        <span className={`text-xs ${status === "healthy" ? "text-green-600" : "text-yellow-600"}`}>
          {status === "healthy" ? "✅ No Throttling" : `⚠ ${throttledCount} throttled · ${totalBlocked} blocked`}
        </span>
      </div>
      {throttledEndpoints.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {throttledEndpoints.map(ep => (
            <div key={ep.path} className="flex justify-between px-4 py-2 text-xs">
              <span className="font-mono text-yellow-600">{ep.path}</span>
              <span className="text-gray-400">{ep.currentRps}/{ep.limit} rps · {ep.blocked} blocked</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
