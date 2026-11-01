"use client";

interface AlertInfo { alert_id: string; metric: string; current_value: number; threshold: number; severity: string; status: string; }
interface Props { alerts: AlertInfo[]; activeCount: number; appName: string; }

const sevStyle: Record<string, string> = { info: "text-blue-600 dark:text-blue-400", warning: "text-yellow-600 dark:text-yellow-400", critical: "text-red-600 dark:text-red-400" };
const sevEmoji: Record<string, string> = { info: "ℹ️", warning: "⚠️", critical: "🚨" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlertCard({ alerts, activeCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Usage Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">{activeCount} active</span>}
      </div>
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No alerts</p>
      ) : (
        <div className="space-y-1.5">
          {alerts.map((a) => (
            <div key={a.alert_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{sevEmoji[a.severity] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{a.metric}</span>
              </div>
              <span className={sevStyle[a.severity] ?? "text-gray-400"}>{a.current_value} / {a.threshold}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
