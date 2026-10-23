"use client";

interface QuickLink { label: string; href: string; icon: string; }
interface Deploy { app: string; version: string; status: string; }
interface Announcement { title: string; type: string; }
interface PortalHomePageProps { greeting: string; stats: { apps: number; installs: number; notifications: number };
  quickLinks: QuickLink[]; recentDeploys: Deploy[]; announcements: Announcement[];
  onNavigate: (href: string) => void; }

export function PortalHomePage({ greeting, stats, quickLinks, recentDeploys, announcements, onNavigate }: PortalHomePageProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{greeting}</h1>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{stats.apps}</p><p className="text-xs text-gray-400">Apps</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{stats.installs.toLocaleString()}</p><p className="text-xs text-gray-400">Installs</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{stats.notifications}</p><p className="text-xs text-gray-400">Notifications</p>
        </div>
      </div>
      {announcements.length > 0 && announcements.map((a, i) => (
        <div key={i} className="rounded-lg bg-blue-50 px-4 py-2 text-sm dark:bg-blue-900/10">📢 {a.title}</div>
      ))}
      <div>
        <h2 className="text-sm font-semibold mb-2">Quick Links</h2>
        <div className="grid grid-cols-3 gap-2">
          {quickLinks.map(l => (
            <button key={l.href} onClick={() => onNavigate(l.href)}
              className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
              <span>{l.icon}</span>{l.label}
            </button>
          ))}
        </div>
      </div>
      {recentDeploys.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Recent Deploys</h2>
          {recentDeploys.map((d, i) => (
            <div key={i} className="flex items-center justify-between rounded border px-3 py-2 text-sm dark:border-gray-700">
              <span>{d.app} v{d.version}</span>
              <span className={d.status === "success" ? "text-green-600" : "text-red-600"}>{d.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
