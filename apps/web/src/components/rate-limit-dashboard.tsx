"use client";

interface EndpointUsage { path: string; limit: number; current: number; }
interface RateLimitDashboardProps { endpoints: EndpointUsage[]; totalUsagePct: number; hotspotCount: number; }

export function RateLimitDashboard({ endpoints, totalUsagePct, hotspotCount }: RateLimitDashboardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Rate Limits</h3>
        <div className="text-right">
          <span className={`text-lg font-bold ${totalUsagePct > 80 ? "text-red-600" : "text-green-600"}`}>{totalUsagePct}%</span>
          {hotspotCount > 0 && <p className="text-xs text-yellow-600">{hotspotCount} hotspot{hotspotCount > 1 ? "s" : ""}</p>}
        </div>
      </div>
      <ul className="mt-3 space-y-2">
        {endpoints.map(e => {
          const pct = Math.round((e.current / Math.max(e.limit, 1)) * 100);
          return (
            <li key={e.path}>
              <div className="flex justify-between text-xs">
                <code>{e.path}</code>
                <span className="text-gray-400">{e.current}/{e.limit} ({pct}%)</span>
              </div>
              <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-full rounded-full ${pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                  style={{ width: `${pct}%` }} />
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
