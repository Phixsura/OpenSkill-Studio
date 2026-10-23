"use client";

interface QuickStat { label: string; value: number; display?: string; icon: string; }
interface RecentApp { id: string; name: string; icon: string; status: string; }
interface QuickAction { label: string; href: string; icon: string; }
interface TopApp { name: string; icon: string; installs: number; }
interface CompleteDashboardProps { greeting: string; orgName: string; orgPlan: string;
  quickStats: QuickStat[]; recentApps: RecentApp[]; quickActions: QuickAction[];
  topApp: TopApp | null; onNavigate: (href: string) => void; onSelectApp: (id: string) => void; }

export function CompleteDashboard({ greeting, orgName, orgPlan, quickStats, recentApps,
  quickActions, topApp, onNavigate, onSelectApp }: CompleteDashboardProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{greeting}</h1>
        <p className="text-sm text-gray-400">{orgName} · <span className="capitalize">{orgPlan}</span> plan</p>
      </div>
      <div className="grid grid-cols-5 gap-3">
        {quickStats.map(s => (
          <div key={s.label} className="rounded-xl border p-3 text-center dark:border-gray-700">
            <span className="text-lg">{s.icon}</span>
            <p className="text-xl font-bold mt-1">{s.display ?? s.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      {topApp && (
        <div className="rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 p-4 dark:from-blue-900/10 dark:to-purple-900/10">
          <p className="text-xs text-gray-400">🏆 Top App</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-2xl">{topApp.icon}</span>
            <span className="text-lg font-bold">{topApp.name}</span>
            <span className="text-sm text-gray-400">{topApp.installs.toLocaleString()} installs</span>
          </div>
        </div>
      )}
      <div className="grid grid-cols-4 gap-2">
        {quickActions.map(a => (
          <button key={a.href} onClick={() => onNavigate(a.href)}
            className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <span>{a.icon}</span>{a.label}
          </button>
        ))}
      </div>
      {recentApps.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Recent Apps</h2>
          <div className="space-y-1">
            {recentApps.map(a => (
              <button key={a.id} onClick={() => onSelectApp(a.id)}
                className="flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-sm text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <span>{a.icon}</span><span className="font-medium">{a.name}</span>
                <span className={`ml-auto rounded px-1.5 py-0.5 text-xs ${a.status === "active" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>{a.status}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
