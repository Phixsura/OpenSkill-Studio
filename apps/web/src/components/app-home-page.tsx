"use client";

interface QuickStat { label: string; value: number; icon: string; display?: string; }
interface Activity { action: string; timestamp: string; }
interface QuickLink { label: string; href: string; icon: string; }
interface AppHeader { name: string; icon: string; version: string; status: string; published: boolean; }
interface AppHomePageProps { header: AppHeader; quickStats: QuickStat[];
  recentActivity: Activity[]; hasUpdate: boolean; quickLinks: QuickLink[];
  onNavigate: (href: string) => void; }

export function AppHomePage({ header, quickStats, recentActivity, hasUpdate, quickLinks, onNavigate }: AppHomePageProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-4xl">{header.icon}</span>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold">{header.name}</h1>
              <span className="text-xs text-gray-400">v{header.version}</span>
              <span className={`rounded px-1.5 py-0.5 text-xs ${header.status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100"}`}>{header.status}</span>
            </div>
            {hasUpdate && <p className="text-xs text-blue-600">Update available</p>}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {quickStats.map(s => (
          <div key={s.label} className="rounded-xl border p-3 text-center dark:border-gray-700">
            <span>{s.icon}</span>
            <p className="text-lg font-bold mt-1">{s.display ?? s.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-4 gap-2">
        {quickLinks.map(l => (
          <button key={l.href} onClick={() => onNavigate(l.href)}
            className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            {l.icon} {l.label}
          </button>
        ))}
      </div>
      {recentActivity.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Recent Activity</h2>
          {recentActivity.map((a, i) => (
            <p key={i} className="text-sm text-gray-500 py-0.5">{a.action}</p>
          ))}
        </div>
      )}
    </div>
  );
}
