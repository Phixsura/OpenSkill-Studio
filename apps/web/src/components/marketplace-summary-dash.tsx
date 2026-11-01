"use client";

interface Category { name: string; icon: string; apps: number; }
interface MarketplaceSummaryDashProps { totalApps: number; totalDevs: number;
  avgRating: number; uptimePct: number; categories: Category[];
  newApps30d: number; devSatisfaction: number; }

export function MarketplaceSummaryDash({ totalApps, totalDevs, avgRating, uptimePct,
  categories, newApps30d, devSatisfaction }: MarketplaceSummaryDashProps) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <p className="text-2xl font-bold">{totalApps}</p><p className="text-xs text-gray-400">Apps</p>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <p className="text-2xl font-bold">{totalDevs}</p><p className="text-xs text-gray-400">Developers</p>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <p className="text-2xl font-bold">⭐ {avgRating}</p><p className="text-xs text-gray-400">Avg Rating</p>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4 text-center">
          <p className="text-2xl font-bold">{uptimePct}%</p><p className="text-xs text-gray-400">Uptime</p>
        </div>
      </div>
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <h3 className="text-sm font-semibold mb-2">Top Categories</h3>
        <div className="flex gap-2 flex-wrap">
          {categories.map(c => (
            <span key={c.name} className="text-xs px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg">
              {c.icon} {c.name} ({c.apps})
            </span>
          ))}
        </div>
      </div>
      <div className="flex gap-4 text-xs text-gray-400 justify-center">
        <span>📈 +{newApps30d} new apps this month</span>
        <span>😊 {devSatisfaction}% developer satisfaction</span>
      </div>
    </div>
  );
}
