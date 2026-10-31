"use client";

interface UsageAnalyticsChartProps { totalEvents: number; uniqueUsers: number;
  byAction: Record<string, number>; topAction: string | null; avgPerDay: number; }

export function UsageAnalyticsChart({ totalEvents, uniqueUsers, byAction, topAction, avgPerDay }: UsageAnalyticsChartProps) {
  const actions = Object.entries(byAction);
  const maxCount = Math.max(...actions.map(([, c]) => c), 1);
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Usage Analytics</h3>
        <span className="text-xs text-gray-400">{totalEvents.toLocaleString()} events · {uniqueUsers} users</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{totalEvents.toLocaleString()}</div>
          <div className="text-[10px] text-gray-400">Total Events</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{avgPerDay}</div>
          <div className="text-[10px] text-gray-400">Avg/Day</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{topAction ?? "—"}</div>
          <div className="text-[10px] text-gray-400">Top Action</div>
        </div>
      </div>
      <div className="p-4 space-y-2">
        {actions.map(([action, count]) => (
          <div key={action}>
            <div className="flex items-center justify-between text-xs mb-0.5">
              <span>{action}</span><span className="text-gray-400">{count}</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(count / maxCount) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
