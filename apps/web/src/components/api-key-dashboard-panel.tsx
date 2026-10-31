"use client";

interface KeyOverview { total: number; active: number; expired: number; revoked: number; expiringSoon: number; unused: number; totalUsage: number; }
interface SecurityAlert { key: string; alert: string; severity: string; }

export function ApiKeyDashboardPanel({ overview, alerts }: { overview: KeyOverview; alerts: SecurityAlert[] }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔑 API Key Dashboard</h2>
      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Active</span>
          <span className="font-bold text-lg text-green-600">{overview.active}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Expiring</span>
          <span className="font-bold text-lg text-yellow-600">{overview.expiringSoon}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Unused</span>
          <span className="font-bold text-lg text-orange-500">{overview.unused}</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Total Usage</span>
          <span className="font-bold text-lg">{overview.totalUsage.toLocaleString()}</span>
        </div>
      </div>
      {alerts.length > 0 && (
        <div className="space-y-1">
          <span className="text-sm font-semibold">⚠ Security Alerts</span>
          {alerts.map((a, i) => (
            <div key={i} className={`text-xs rounded-lg border-l-4 p-2 ${a.severity === "high" ? "border-red-500 bg-red-50 dark:bg-red-900/10" : "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10"}`}>
              <b>{a.key}</b>: {a.alert}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
