"use client";

interface Alert { id: string; metric: string; usagePct: number; currentUsage: number; limit: number; triggeredAt: string; }
interface Rule { id: string; metric: string; thresholdPct: number; enabled: boolean; }
interface Props { alerts: Alert[]; rules: Rule[]; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlertCard({ alerts, rules, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Quota Alerts</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId} · {rules.length} rules</p>
      </div>
      {alerts.length > 0 && (
        <div className="mb-3 space-y-1">
          {alerts.slice(0, 5).map((a) => (
            <div key={a.id} className="rounded bg-red-50 px-2 py-1 text-[10px] dark:bg-red-900/20">
              <div className="flex justify-between">
                <span className="font-medium text-red-700 dark:text-red-400">{a.metric} at {a.usagePct}%</span>
                <span className="text-gray-400">{a.triggeredAt}</span>
              </div>
              <span className="text-red-500">{a.currentUsage.toLocaleString()} / {a.limit.toLocaleString()}</span>
            </div>
          ))}
        </div>
      )}
      {rules.length === 0 && alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quota alert rules</p>
      ) : (
        <div className="space-y-0.5">
          {rules.map((r) => (
            <div key={r.id} className="flex items-center justify-between text-[10px] text-gray-500">
              <span>{r.metric} ≥ {r.thresholdPct}%</span>
              <span className={r.enabled ? "text-green-500" : "text-gray-400"}>{r.enabled ? "ON" : "OFF"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
