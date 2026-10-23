"use client";

interface InstallAnalyticsDashboardProps { totalInstalls: number; bySource: Record<string, number>;
  byPlatform: Record<string, number>; topSource: string | null; }

const sourceIcon: Record<string, string> = {
  search: "🔍", referral: "🔗", direct: "🌐", social: "📱", email: "📧", ad: "📢",
};

export function InstallAnalyticsDashboard({ totalInstalls, bySource, byPlatform, topSource }: InstallAnalyticsDashboardProps) {
  const maxSource = Math.max(...Object.values(bySource), 1);
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Install Analytics</h2>
        <span className="text-xl font-bold">{totalInstalls.toLocaleString()}</span>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-500">By Source</h3>
          <div className="mt-2 space-y-1.5">
            {Object.entries(bySource).map(([src, count]) => (
              <div key={src}>
                <div className="flex justify-between text-xs">
                  <span>{sourceIcon[src] ?? "📌"} {src}</span>
                  <span className="text-gray-400">{count}</span>
                </div>
                <div className="mt-0.5 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className="h-full rounded-full bg-blue-500"
                    style={{ width: `${(count / maxSource) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-500">By Platform</h3>
          <div className="mt-2 space-y-2">
            {Object.entries(byPlatform).map(([plat, count]) => (
              <div key={plat} className="flex items-center justify-between rounded bg-gray-50 p-2 dark:bg-gray-800">
                <span className="text-sm capitalize">{plat}</span>
                <span className="font-bold">{count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      {topSource && (
        <p className="text-center text-xs text-gray-400">Top source: <strong>{topSource}</strong></p>
      )}
    </div>
  );
}
