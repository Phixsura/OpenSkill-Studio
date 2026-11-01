"use client";

interface AlertInfo { alert_id: string; consumer_id: string; metric: string; usage_pct: number; threshold_pct: number; acknowledged: boolean; }
interface Props { alerts: AlertInfo[]; unacknowledgedCount: number; appName: string; }

const pctColor = (p: number) => p >= 95 ? "text-red-600 dark:text-red-400" : p >= 75 ? "text-orange-600 dark:text-orange-400" : "text-yellow-600 dark:text-yellow-400";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerUsageLimitAlertCard({ alerts, unacknowledgedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚠️ Usage Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {unacknowledgedCount > 0 && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">{unacknowledgedCount} unacked</span>}
      </div>
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No usage alerts</p>
      ) : (
        <div className="space-y-1">
          {alerts.map((a) => (
            <div key={a.alert_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.consumer_id} / {a.metric}</span>
              <span className={pctColor(a.usage_pct)}>{a.usage_pct}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
