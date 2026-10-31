"use client";

interface DevAnalyticsOverviewProps { appCount: number; installsDisplay: string;
  apiDisplay: string; revenueDisplay: string; avgRating: number;
  topApp: { name: string; installs: number } | null; growthAreas: string[]; period: string; }

export function DevAnalyticsOverview({ appCount, installsDisplay, apiDisplay, revenueDisplay,
  avgRating, topApp, growthAreas, period }: DevAnalyticsOverviewProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📊 Developer Analytics</h3>
        <span className="text-xs text-gray-400">{period}</span>
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{appCount}</p><p className="text-xs text-gray-400">Apps</p></div>
        <div><p className="text-lg font-bold">{installsDisplay}</p><p className="text-xs text-gray-400">Installs</p></div>
        <div><p className="text-lg font-bold">{apiDisplay}</p><p className="text-xs text-gray-400">API Calls</p></div>
        <div><p className="text-lg font-bold">{revenueDisplay}</p><p className="text-xs text-gray-400">Revenue</p></div>
      </div>
      {topApp && <p className="text-xs text-gray-400 mb-2">🏆 Top: {topApp.name} ({topApp.installs.toLocaleString()} installs)</p>}
      {growthAreas.length > 0 && (
        <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded text-xs text-yellow-700">
          {growthAreas.map((a, i) => <p key={i}>📈 {a}</p>)}
        </div>
      )}
    </div>
  );
}
