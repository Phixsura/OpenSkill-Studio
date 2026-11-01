"use client";

interface TopAction { action: string; count: number; }
interface EngagementMetricsCardProps { period: string; totalEvents: number;
  avgDau: number; avgWau: number; stickinessPct: number; topActions: TopAction[]; }

export function EngagementMetricsCard({ period, totalEvents, avgDau, avgWau, stickinessPct, topActions }: EngagementMetricsCardProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">User Engagement</h3>
        <span className="text-xs text-gray-400">{period} · {totalEvents.toLocaleString()} events</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{avgDau}</p><p className="text-xs text-gray-400">Avg DAU</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{avgWau}</p><p className="text-xs text-gray-400">Avg WAU</p>
        </div>
        <div className="rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-xl font-bold">{stickinessPct}%</p><p className="text-xs text-gray-400">Stickiness</p>
        </div>
      </div>
      <div>
        <p className="text-xs font-semibold text-gray-400 mb-1">Top Actions</p>
        {topActions.map(a => (
          <div key={a.action} className="flex justify-between text-sm py-0.5">
            <span className="capitalize">{a.action}</span>
            <span className="text-gray-400">{a.count.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
