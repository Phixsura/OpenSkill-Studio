"use client";

interface QuickAction { label: string; icon: string; action: string; }
interface RecentDeploy { app: string; version: string; status: string; time: string; }
interface DevConsoleDashboardProps {
  devName: string; plan: string; verified: boolean;
  totalApps: number; installsDisplay: string; avgRating: number;
  apiDisplay: string; openIssues: number;
  recentDeploys: RecentDeploy[]; quickActions: QuickAction[];
  onAction: (action: string) => void; }

export function DevConsoleDashboard({ devName, plan, verified, totalApps,
  installsDisplay, avgRating, apiDisplay, openIssues, recentDeploys,
  quickActions, onAction }: DevConsoleDashboardProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">Welcome back, {devName}</h1>
          <div className="flex gap-2 text-xs mt-1">
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 uppercase">{plan}</span>
            {verified && <span className="text-blue-500">✓ Verified</span>}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {[
          { icon: "📱", value: String(totalApps), label: "Apps" },
          { icon: "📥", value: installsDisplay, label: "Installs" },
          { icon: "📡", value: apiDisplay, label: "API Calls" },
          { icon: "🐛", value: String(openIssues), label: "Issues" },
        ].map(s => (
          <div key={s.label} className="rounded-xl border dark:border-gray-700 p-4 text-center">
            <p className="text-lg mb-0.5">{s.icon}</p>
            <p className="text-xl font-bold">{s.value}</p>
            <p className="text-xs text-gray-400">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <h3 className="text-sm font-semibold mb-2">⚡ Quick Actions</h3>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map(a => (
              <button key={a.action} onClick={() => onAction(a.action)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm">
                <span>{a.icon}</span>{a.label}
              </button>
            ))}
          </div>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-4">
          <h3 className="text-sm font-semibold mb-2">🚀 Recent Deploys</h3>
          {recentDeploys.map((d, i) => (
            <div key={i} className="flex justify-between text-sm py-1">
              <span>{d.app} v{d.version}</span>
              <span className={`text-xs ${d.status === "success" ? "text-green-600" : "text-red-500"}`}>{d.status} · {d.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
