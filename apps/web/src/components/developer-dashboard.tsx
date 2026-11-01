"use client";

interface QuickStat { label: string; value: number; icon: string; }
interface AppSummary { id: string; name: string; icon: string; status: string; downloads: number; }
interface DeveloperDashboardProps { greeting: string; quickStats: QuickStat[];
  recentApps: AppSummary[]; hasApps: boolean; onSelectApp: (id: string) => void; }

export function DeveloperDashboard({ greeting, quickStats, recentApps, hasApps, onSelectApp }: DeveloperDashboardProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{greeting}</h1>
      <div className="grid grid-cols-4 gap-3">
        {quickStats.map(s => (
          <div key={s.label} className="rounded-xl border p-4 text-center dark:border-gray-700">
            <span className="text-xl">{s.icon}</span>
            <p className="text-2xl font-bold mt-1">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      {hasApps ? (
        <div>
          <h2 className="text-sm font-semibold mb-3">Recent Apps</h2>
          <div className="space-y-2">
            {recentApps.map(a => (
              <button key={a.id} onClick={() => onSelectApp(a.id)}
                className="flex w-full items-center justify-between rounded-lg border px-4 py-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{a.icon}</span>
                  <span className="font-medium">{a.name}</span>
                </div>
                <span className="text-xs text-gray-400">{a.downloads.toLocaleString()} downloads</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <span className="text-4xl">📦</span>
          <p className="mt-2 text-sm text-gray-500">No apps yet. Create your first app!</p>
        </div>
      )}
    </div>
  );
}
