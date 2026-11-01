"use client";

interface TopAction { action: string; count: number; }
interface FunnelStep { step: string; count: number; dropOffPct: number; conversionPct: number; }
interface UsageAnalyticsDashboardProps { totalEvents: number; uniqueUsers: number;
  eventsPerUser: number; topActions: TopAction[]; funnel: FunnelStep[]; overallConversion: number; }

export function UsageAnalyticsDashboard({ totalEvents, uniqueUsers, eventsPerUser, topActions, funnel, overallConversion }: UsageAnalyticsDashboardProps) {
  return (
    <div className="space-y-5">
      <h3 className="text-sm font-semibold">Usage Analytics</h3>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{totalEvents.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Events</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{uniqueUsers.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Users</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{eventsPerUser}</p>
          <p className="text-xs text-gray-400">Events/User</p>
        </div>
      </div>
      <div>
        <p className="text-xs font-semibold text-gray-400 mb-2">Conversion Funnel ({overallConversion}%)</p>
        {funnel.map((s, i) => (
          <div key={i} className="flex items-center gap-2 mb-1">
            <div className="flex-1">
              <div className="flex justify-between text-xs mb-0.5">
                <span>{s.step}</span><span className="text-gray-400">{s.count.toLocaleString()}</span>
              </div>
              <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${s.conversionPct}%` }} />
              </div>
            </div>
            {s.dropOffPct > 0 && <span className="text-xs text-red-500 w-12 text-right">-{s.dropOffPct}%</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
