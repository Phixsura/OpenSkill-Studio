"use client";

interface AlertInfo { alert_id: string; consumer_id: string; metric: string; deviation_pct: number; severity: string; }
interface Props { alerts: AlertInfo[]; totalAlerts: number; appName: string; }

const sevColor: Record<string, string> = { low: "text-yellow-600 dark:text-yellow-400", medium: "text-orange-600 dark:text-orange-400", high: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiAnomalyDetectorCard({ alerts, totalAlerts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Anomaly Detector</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {totalAlerts > 0 && <span className="rounded-full bg-orange-100 px-2 py-0.5 text-[10px] font-medium text-orange-700 dark:bg-orange-900/30 dark:text-orange-400">{totalAlerts} anomalies</span>}
      </div>
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No anomalies detected</p>
      ) : (
        <div className="space-y-1">
          {alerts.map((a) => (
            <div key={a.alert_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{a.consumer_id} / {a.metric}</span>
              <span className={sevColor[a.severity] ?? "text-gray-400"}>↑{a.deviation_pct}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
