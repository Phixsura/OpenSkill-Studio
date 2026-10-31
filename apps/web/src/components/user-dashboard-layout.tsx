"use client";

interface QuickStat { icon: string; value: string; label: string; }
interface Alert { type: string; message: string; }
interface UserDashboardLayoutProps { greeting: string; orgName: string; plan: string;
  quickStats: QuickStat[]; alerts: Alert[]; children: React.ReactNode; }

export function UserDashboardLayout({ greeting, orgName, plan, quickStats, alerts, children }: UserDashboardLayoutProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">{greeting}</h1>
          <p className="text-xs text-gray-400">{orgName} · <span className="capitalize">{plan}</span></p>
        </div>
      </div>
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((a, i) => (
            <div key={i} className={`rounded-lg p-3 text-sm ${a.type === "warning" ? "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/20" : "bg-blue-50 text-blue-700 dark:bg-blue-900/20"}`}>
              {a.message}
            </div>
          ))}
        </div>
      )}
      <div className="grid grid-cols-6 gap-3">
        {quickStats.map(s => (
          <div key={s.label} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <p className="text-lg">{s.icon}</p>
            <p className="text-lg font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      {children}
    </div>
  );
}
