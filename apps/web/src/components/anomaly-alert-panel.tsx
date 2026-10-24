"use client";
interface Alert { name: string; metric: string; value: number; threshold: number; severity: string; }
interface AnomalyAlertPanelProps { alerts: Alert[]; activeCount: number; totalFired: number; }
const SEV_COLOR: Record<string, string> = { critical: "text-red-600", warning: "text-yellow-600", info: "text-blue-500" };
export function AnomalyAlertPanel({ alerts, activeCount, totalFired }: AnomalyAlertPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚨 Anomaly Alerts</h3>
        <span className={`text-xs font-bold ${activeCount > 0 ? "text-red-500" : "text-green-600"}`}>
          {activeCount > 0 ? `🔔 ${activeCount} active` : "✅ Clear"} · {totalFired} total
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {alerts.map(a => (
          <div key={a.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className={`font-semibold ${SEV_COLOR[a.severity] ?? ""}`}>{a.name}</span>
            <span className="text-gray-400">{a.metric}: {a.value} (threshold: {a.threshold})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
