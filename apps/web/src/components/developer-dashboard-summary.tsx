"use client";

interface Trend { metric: string; current: number; change: number; trend: "up" | "down" | "flat"; }
interface Alert { severity: string; message: string; action: string; }

const trendIcons: Record<string, string> = { up: "📈", down: "📉", flat: "➡️" };
const trendColors: Record<string, string> = { up: "text-green-600", down: "text-red-600", flat: "text-gray-500" };
const metricLabels: Record<string, string> = { installs: "Installs", revenue_cents: "Revenue", api_calls: "API Calls", active_users: "Active Users" };
const alertColors: Record<string, string> = { critical: "border-red-500 bg-red-50 dark:bg-red-900/10", warning: "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10", info: "border-blue-400 bg-blue-50 dark:bg-blue-900/10" };

export function DeveloperDashboardSummary({
  trends, alerts, healthScore, totalInstalls, errorRate, avgRating,
}: {
  trends: Trend[]; alerts: Alert[]; healthScore: number;
  totalInstalls: number; errorRate: number; avgRating: number;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📊 Developer Dashboard</h2>

      <div className="grid grid-cols-4 gap-2 text-center">
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Health</span>
          <span className={`text-xl font-bold ${healthScore >= 90 ? "text-green-600" : "text-yellow-600"}`}>{healthScore}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Installs</span>
          <span className="text-xl font-bold">{totalInstalls.toLocaleString()}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Error Rate</span>
          <span className={`text-xl font-bold ${errorRate > 5 ? "text-red-600" : "text-green-600"}`}>{errorRate}%</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3">
          <span className="text-xs text-gray-500 block">Rating</span>
          <span className="text-xl font-bold text-yellow-500">★ {avgRating}</span>
        </div>
      </div>

      {trends.length > 0 && (
        <div className="flex gap-3">
          {trends.map((t) => (
            <div key={t.metric} className="flex items-center gap-1 text-xs">
              <span>{trendIcons[t.trend]}</span>
              <span className="text-gray-500">{metricLabels[t.metric] || t.metric}</span>
              <span className={`font-bold ${trendColors[t.trend]}`}>{t.change > 0 ? "+" : ""}{t.change}%</span>
            </div>
          ))}
        </div>
      )}

      {alerts.length > 0 && (
        <div className="space-y-1">
          {alerts.map((a, i) => (
            <div key={i} className={`rounded-lg border-l-4 p-2 text-sm ${alertColors[a.severity]}`}>
              <span className="font-medium">{a.message}</span>
              {a.action && <span className="text-xs text-gray-500 ml-2">→ {a.action}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
