"use client";

interface QuickLink { label: string; icon: string; url: string; }
interface RecentApp { id: string; name: string; installs: number; }
interface Stats { apps: number; installs: number; revenue: number; avg_rating: number; }
interface DeveloperPortalHomeProps { greeting: string; stats: Stats; recentApps: RecentApp[];
  notifications: number; quickLinks: QuickLink[]; onNavigate: (url: string) => void; }

export function DeveloperPortalHome({ greeting, stats, recentApps, notifications, quickLinks, onNavigate }: DeveloperPortalHomeProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{greeting}</h1>
        {notifications > 0 && (
          <span className="flex h-6 items-center rounded-full bg-red-500 px-2.5 text-xs text-white">
            🔔 {notifications}
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Apps", value: stats.apps, icon: "📦" },
          { label: "Installs", value: stats.installs.toLocaleString(), icon: "📥" },
          { label: "Revenue", value: `$${stats.revenue.toLocaleString()}`, icon: "💰" },
          { label: "Rating", value: `⭐ ${stats.avg_rating}`, icon: "" },
        ].map(s => (
          <div key={s.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className="text-xl font-bold">{s.icon} {s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <h2 className="text-sm font-semibold text-gray-500">Recent Apps</h2>
          <div className="mt-2 space-y-1.5">
            {recentApps.map(a => (
              <button key={a.id} onClick={() => onNavigate(`/apps/${a.id}`)}
                className="flex w-full items-center justify-between rounded border px-3 py-2 text-left text-sm dark:border-gray-700">
                <span className="font-medium">{a.name}</span>
                <span className="text-xs text-gray-400">{a.installs.toLocaleString()} installs</span>
              </button>
            ))}
          </div>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-gray-500">Quick Links</h2>
          <div className="mt-2 grid grid-cols-2 gap-1.5">
            {quickLinks.map(l => (
              <button key={l.url} onClick={() => onNavigate(l.url)}
                className="rounded border px-3 py-2 text-left text-xs hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                {l.icon} {l.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
