"use client";

interface AlertInfo { alert_id: string; consumer_id: string; resource: string; threshold_pct: number; current_usage_pct: number; triggered: boolean; }
interface Props { alerts: AlertInfo[]; triggeredCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiUsageQuotaAlertCard({ alerts, triggeredCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Quota Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {triggeredCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{triggeredCount} firing</span>}
      </div>
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No quota alerts</p>
      ) : (
        <div className="space-y-2">
          {alerts.map((a) => (
            <div key={a.alert_id}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{a.consumer_id} · {a.resource}</span>
                <span className={a.triggered ? "text-red-500 font-bold" : "text-gray-400"}>{a.current_usage_pct}% / {a.threshold_pct}%</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${a.triggered ? "bg-red-500" : a.current_usage_pct >= a.threshold_pct * 0.8 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${Math.min(a.current_usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
