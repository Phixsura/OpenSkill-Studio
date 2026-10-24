"use client";

interface QuickAction { id: string; label: string; icon: string; }
interface DashboardOverview { total_apps: number; active_apps: number; total_installs: number;
  total_revenue: number; avg_rating: number; notifications: number; }
interface Analytics { dau: number; wau: number; mau: number; api_calls_today: number; error_rate: number; }
interface TopApp { name: string; installs: number; }
interface Developer { name: string; verified: boolean; plan: string; }
interface FullDeveloperDashboardProps { developer: Developer; overview: DashboardOverview;
  topApp: TopApp | null; analytics: Analytics; quickActions: QuickAction[];
  onAction: (id: string) => void; }

export function FullDeveloperDashboard({ developer, overview, topApp, analytics, quickActions, onAction }: FullDeveloperDashboardProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Welcome, {developer.name}!</h1>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            {developer.verified && <span className="text-blue-500">✓ Verified</span>}
            <span className="capitalize">{developer.plan} plan</span>
          </div>
        </div>
        {overview.notifications > 0 && (
          <span className="flex h-7 items-center rounded-full bg-red-500 px-3 text-xs text-white">🔔 {overview.notifications}</span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        {[
          { label: "Apps", value: overview.total_apps, icon: "📦" },
          { label: "Installs", value: overview.total_installs.toLocaleString(), icon: "📥" },
          { label: "Revenue", value: `$${overview.total_revenue.toLocaleString()}`, icon: "💰" },
          { label: "Rating", value: `⭐ ${overview.avg_rating}`, icon: "" },
          { label: "DAU", value: analytics.dau.toLocaleString(), icon: "👥" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className="text-xl font-bold">{s.icon} {s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {topApp && (
          <div className="rounded-lg border p-4 dark:border-gray-700">
            <h3 className="text-sm font-medium text-gray-400">🏆 Top App</h3>
            <p className="mt-1 text-lg font-bold">{topApp.name}</p>
            <p className="text-sm text-gray-400">{topApp.installs.toLocaleString()} installs</p>
          </div>
        )}
        <div className="rounded-lg border p-4 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-400">Quick Actions</h3>
          <div className="mt-2 grid grid-cols-2 gap-1.5">
            {quickActions.map(a => (
              <button key={a.id} onClick={() => onAction(a.id)}
                className="rounded border px-2 py-1.5 text-xs hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800">
                {a.icon} {a.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
