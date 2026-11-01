"use client";

interface DashboardOverview {
  total_api_calls: number;
  active_developers: number;
  webhook_success_rate: number;
  active_incidents: number;
  uptime_pct: number;
  error_rate: number;
}

interface APIDeveloperDashboardCardProps {
  overview: DashboardOverview;
  appName: string;
}

export default function APIDeveloperDashboardCard({ overview, appName }: APIDeveloperDashboardCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏠 Developer Dashboard</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="rounded-lg bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{overview.total_api_calls.toLocaleString()}</p>
          <p className="text-[9px] text-gray-500">API Calls</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{overview.active_developers}</p>
          <p className="text-[9px] text-gray-500">Developers</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${overview.uptime_pct >= 99.9 ? "text-green-600" : "text-yellow-600"}`}>{overview.uptime_pct}%</p>
          <p className="text-[9px] text-gray-500">Uptime</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-2 dark:bg-gray-800">
          <p className="text-lg font-bold text-green-600">{overview.webhook_success_rate}%</p>
          <p className="text-[9px] text-gray-500">Webhooks</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${overview.active_incidents > 0 ? "text-red-500" : "text-green-600"}`}>{overview.active_incidents}</p>
          <p className="text-[9px] text-gray-500">Incidents</p>
        </div>
        <div className="rounded-lg bg-gray-50 py-2 dark:bg-gray-800">
          <p className={`text-lg font-bold ${overview.error_rate > 1 ? "text-red-500" : "text-gray-900 dark:text-gray-100"}`}>{overview.error_rate}%</p>
          <p className="text-[9px] text-gray-500">Error Rate</p>
        </div>
      </div>
    </div>
  );
}
