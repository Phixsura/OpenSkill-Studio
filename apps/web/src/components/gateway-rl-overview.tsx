"use client";

interface RouteRL { path: string; method: string; requests: number; blocked: number;
  limit: number; usagePct: number; status: string; }
interface GatewayRlOverviewProps { totalRequests: number; totalBlocked: number;
  blockRateDisplay: string; routes: RouteRL[]; exceededCount: number; }

export function GatewayRlOverview({ totalRequests, totalBlocked, blockRateDisplay, routes, exceededCount }: GatewayRlOverviewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Rate Limits Overview</h3>
        <div className="flex gap-2 text-xs">
          <span>{totalRequests.toLocaleString()} requests</span>
          <span className="text-red-500">{totalBlocked} blocked ({blockRateDisplay})</span>
          {exceededCount > 0 && <span className="px-1.5 py-0.5 rounded bg-red-100 text-red-700">{exceededCount} exceeded</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {routes.map(r => (
          <div key={`${r.method}-${r.path}`} className="px-4 py-2.5 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-blue-600 mr-1">{r.method}</span>
              <span className="text-sm font-mono">{r.path}</span>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-gray-400">{r.requests}/{r.limit}</span>
              <div className="w-20 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${r.status === "exceeded" ? "bg-red-500" : r.status === "warning" ? "bg-yellow-500" : "bg-green-500"}`}
                     style={{ width: `${Math.min(r.usagePct, 100)}%` }} />
              </div>
              {r.blocked > 0 && <span className="text-red-500">{r.blocked} blocked</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
