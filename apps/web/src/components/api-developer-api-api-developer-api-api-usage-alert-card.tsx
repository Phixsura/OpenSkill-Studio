"use client";

interface AlertInfo { alert_id: string; metric: string; threshold: number; operator: string; current_value: number; triggered: boolean; }
interface Props { alerts: AlertInfo[]; triggeredCount: number; appName: string; }

const opSymbol: Record<string, string> = { gt: ">", lt: "<", gte: "≥", lte: "≤" };

export default function APIDeveloperAPIApiDeveloperApiApiUsageAlertCard({ alerts, triggeredCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚨 Usage Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {triggeredCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{triggeredCount} firing</span>}
      </div>
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No alerts configured</p>
      ) : (
        <div className="space-y-1.5">
          {alerts.map((a) => (
            <div key={a.alert_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${a.triggered ? "bg-red-500 animate-pulse" : "bg-green-500"}`} />
                <span className="text-gray-700 dark:text-gray-300">{a.metric}</span>
              </div>
              <span className="text-gray-400">{a.current_value} {opSymbol[a.operator]} {a.threshold}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
