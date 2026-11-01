"use client";

interface PlatformOverviewDashProps { healthScore: number; status: string;
  apps: { total: number; active: number; healthyPct: number };
  infra: { services: number; uptimePct: number; incidents: number };
  users: { total: number; activeToday: number; satisfactionPct: number }; }

const STATUS_COLORS: Record<string, string> = {
  healthy: "text-green-600", degraded: "text-yellow-600", critical: "text-red-600",
};

export function PlatformOverviewDash({ healthScore, status, apps, infra, users }: PlatformOverviewDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-6 text-center border-b dark:border-gray-700">
        <div className={`text-4xl font-bold ${STATUS_COLORS[status] ?? ""}`}>{healthScore}</div>
        <div className="text-sm text-gray-400 mt-1">Platform Health Score</div>
        <div className={`text-xs font-medium mt-1 capitalize ${STATUS_COLORS[status] ?? ""}`}>{status}</div>
      </div>
      <div className="grid grid-cols-3 divide-x dark:divide-gray-700">
        <div className="p-4 text-center">
          <div className="text-xs text-gray-400 mb-1">Apps</div>
          <div className="text-lg font-bold">{apps.active}/{apps.total}</div>
          <div className="text-[10px] text-gray-400">{apps.healthyPct}% healthy</div>
        </div>
        <div className="p-4 text-center">
          <div className="text-xs text-gray-400 mb-1">Infrastructure</div>
          <div className="text-lg font-bold">{infra.uptimePct}%</div>
          <div className="text-[10px] text-gray-400">{infra.services} services · {infra.incidents} incidents</div>
        </div>
        <div className="p-4 text-center">
          <div className="text-xs text-gray-400 mb-1">Users</div>
          <div className="text-lg font-bold">{users.activeToday.toLocaleString()}</div>
          <div className="text-[10px] text-gray-400">{users.satisfactionPct}% satisfaction</div>
        </div>
      </div>
    </div>
  );
}
