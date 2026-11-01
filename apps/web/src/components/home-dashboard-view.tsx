"use client";

interface Stat { icon: string; label: string; value: string; }
interface TopApp { name: string; installs: number; }
interface HomeDashboardViewProps { greeting: string; plan: string; stats: Stat[];
  topApps: TopApp[]; quickActions: string[]; onAction: (a: string) => void; }

export function HomeDashboardView({ greeting, plan, stats, topApps, quickActions, onAction }: HomeDashboardViewProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{greeting}</h1>
        <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700 capitalize">{plan}</span>
      </div>
      <div className="grid grid-cols-3 gap-3">
        {stats.map(s => (
          <div key={s.label} className="rounded-xl border dark:border-gray-700 p-4 text-center">
            <p className="text-lg">{s.icon}</p>
            <p className="text-xl font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        {quickActions.map(a => (
          <button key={a} onClick={() => onAction(a)}
            className="text-sm px-3 py-1.5 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">{a}</button>
        ))}
      </div>
      {topApps.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold mb-2">🏆 Top Apps</h3>
          {topApps.map(a => (
            <div key={a.name} className="flex justify-between text-sm py-1">
              <span>{a.name}</span>
              <span className="text-gray-400">{a.installs.toLocaleString()} installs</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
