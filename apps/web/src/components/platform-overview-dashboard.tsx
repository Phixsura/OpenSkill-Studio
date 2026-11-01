"use client";

interface PlatformStats {
  totalExtensions: number;
  activeInstalls: number;
  totalDevelopers: number;
  monthlyRevenueCents: number;
  apiCallsToday: number;
  uptimePercent: number;
  avgResponseMs: number;
  openIssues: number;
}

interface SystemHealth {
  name: string;
  status: "healthy" | "degraded" | "down";
}

function fmt(cents: number) {
  return `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 0 })}`;
}

const healthIcons: Record<string, string> = {
  healthy: "🟢", degraded: "🟡", down: "🔴",
};

export function PlatformOverviewDashboard({
  stats,
  systems,
}: {
  stats: PlatformStats;
  systems: SystemHealth[];
}) {
  const healthyCount = systems.filter((s) => s.status === "healthy").length;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🏠 Platform Overview</h2>

      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Extensions</span>
          <span className="text-xl font-bold">{stats.totalExtensions}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Active Installs</span>
          <span className="text-xl font-bold text-green-600">{stats.activeInstalls.toLocaleString()}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Revenue</span>
          <span className="text-xl font-bold text-blue-600">{fmt(stats.monthlyRevenueCents)}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Developers</span>
          <span className="text-xl font-bold">{stats.totalDevelopers}</span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">API Calls Today</span>
          <span className="text-sm font-bold">{stats.apiCallsToday.toLocaleString()}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">Uptime</span>
          <span className={`text-sm font-bold ${stats.uptimePercent >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>
            {stats.uptimePercent}%
          </span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">Avg Response</span>
          <span className="text-sm font-bold">{stats.avgResponseMs}ms</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2 text-center">
          <span className="text-xs text-gray-400 block">Open Issues</span>
          <span className={`text-sm font-bold ${stats.openIssues > 0 ? "text-yellow-600" : "text-green-600"}`}>
            {stats.openIssues}
          </span>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-semibold">System Health</span>
          <span className="text-xs text-gray-500">{healthyCount}/{systems.length} healthy</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {systems.map((sys) => (
            <div key={sys.name} className="flex items-center gap-1 text-xs rounded-lg border dark:border-gray-700 px-2 py-1">
              <span>{healthIcons[sys.status]}</span>
              <span>{sys.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
