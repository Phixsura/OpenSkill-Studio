"use client";

interface Kpi { label: string; value: number; display?: string; icon: string; }
interface Health { overall: string; apps: string; webhooks: string; deploys: string; }
interface RecentApp { id: string; name: string; icon: string; }
interface UnifiedDashboardProps { greeting: string; org: string; plan: string;
  health: Health; kpis: Kpi[]; notifications: number; recentApps: RecentApp[];
  onNavigate: (href: string) => void; }

const healthDot: Record<string, string> = { healthy: "bg-green-500", attention: "bg-yellow-500" };

export function UnifiedDashboard({ greeting, org, plan, health, kpis, notifications,
  recentApps, onNavigate }: UnifiedDashboardProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{greeting}</h1>
          <p className="text-sm text-gray-400">{org} · <span className="capitalize">{plan}</span></p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`h-3 w-3 rounded-full ${healthDot[health.overall] ?? "bg-gray-400"}`} />
          {notifications > 0 && (
            <button onClick={() => onNavigate("/notifications")}
              className="rounded-full bg-red-500 px-2.5 py-0.5 text-xs text-white">{notifications}</button>
          )}
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {kpis.map(k => (
          <div key={k.label} className="rounded-xl border p-4 text-center dark:border-gray-700">
            <span className="text-xl">{k.icon}</span>
            <p className="text-2xl font-bold mt-1">{k.display ?? k.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{k.label}</p>
          </div>
        ))}
      </div>
      {recentApps.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-2">Recent Apps</h2>
          <div className="flex gap-2">
            {recentApps.map(a => (
              <button key={a.id} onClick={() => onNavigate(`/apps/${a.id}`)}
                className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm dark:border-gray-700">
                {a.icon} {a.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
