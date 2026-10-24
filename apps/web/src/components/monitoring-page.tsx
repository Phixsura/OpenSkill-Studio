"use client";

interface Metric { label: string; value: number; display: string; icon: string; }
interface Alert { title: string; severity: string; }
interface MonitoringPageProps { appName: string; health: string; healthIcon: string;
  metrics: Metric[]; activeAlerts: Alert[]; checkedAt: string; }

const sevBg: Record<string, string> = {
  critical: "bg-red-50 border-red-300 dark:bg-red-900/10",
  warning: "bg-yellow-50 border-yellow-300 dark:bg-yellow-900/10",
};

export function MonitoringPage({ appName, health, healthIcon, metrics, activeAlerts, checkedAt }: MonitoringPageProps) {
  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📡 {appName} — Monitoring</h2>
        <div className="flex items-center gap-2">
          <span>{healthIcon}</span>
          <span className="text-sm font-medium capitalize">{health}</span>
          <span className="text-xs text-gray-400">· {new Date(checkedAt).toLocaleTimeString()}</span>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {metrics.map(m => (
          <div key={m.label} className="rounded-xl border p-4 text-center dark:border-gray-700">
            <span className="text-lg">{m.icon}</span>
            <p className="text-xl font-bold mt-1">{m.display}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
      {activeAlerts.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">🚨 Active Alerts ({activeAlerts.length})</h3>
          {activeAlerts.map((a, i) => (
            <div key={i} className={`rounded-lg border p-3 ${sevBg[a.severity] ?? ""}`}>
              <p className="text-sm font-medium">{a.title}</p>
              <p className="text-xs text-gray-400 capitalize">{a.severity}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
