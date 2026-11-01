"use client";

interface UsageMetrics {
  dailyActiveUsers: number;
  weeklyActiveUsers: number;
  monthlyActiveUsers: number;
  totalApiCalls: number;
  avgSessionMinutes: number;
  retentionRate: number;
}

interface UsageTrend {
  date: string;
  users: number;
  apiCalls: number;
}

export function ExtensionUsageDashboard({
  metrics,
  trends,
  extensionName,
}: {
  metrics: UsageMetrics;
  trends: UsageTrend[];
  extensionName: string;
}) {
  const dauWauRatio = metrics.weeklyActiveUsers > 0
    ? Math.round((metrics.dailyActiveUsers / metrics.weeklyActiveUsers) * 100) : 0;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📈 {extensionName} Usage</h2>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">DAU</span>
          <span className="text-xl font-bold text-blue-600">{metrics.dailyActiveUsers.toLocaleString()}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">WAU</span>
          <span className="text-xl font-bold">{metrics.weeklyActiveUsers.toLocaleString()}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">MAU</span>
          <span className="text-xl font-bold">{metrics.monthlyActiveUsers.toLocaleString()}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">DAU/WAU</span>
          <span className={`text-sm font-bold ${dauWauRatio > 40 ? "text-green-600" : "text-yellow-600"}`}>{dauWauRatio}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">Avg Session</span>
          <span className="text-sm font-bold">{metrics.avgSessionMinutes}min</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">Retention</span>
          <span className={`text-sm font-bold ${metrics.retentionRate > 40 ? "text-green-600" : "text-red-600"}`}>
            {metrics.retentionRate}%
          </span>
        </div>
      </div>

      <div>
        <span className="text-sm font-semibold">7-Day Trend</span>
        <div className="mt-2 flex items-end gap-1 h-20">
          {trends.map((t) => {
            const maxUsers = Math.max(...trends.map((tr) => tr.users), 1);
            const height = Math.max((t.users / maxUsers) * 100, 5);
            return (
              <div key={t.date} className="flex-1 flex flex-col items-center gap-0.5">
                <div className="w-full bg-blue-500 rounded-t" style={{ height: `${height}%` }} />
                <span className="text-[9px] text-gray-400">{t.date}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
