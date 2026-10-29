"use client";

interface AlertInfo { alert_id: string; destination: string; threshold_ms: number; current_avg_ms: number; triggered: boolean; trigger_count: number; }
interface Props { alerts: AlertInfo[]; appName: string; }

export default function APIWebhookLatencyAlertCard({ alerts, appName }: Props) {
  const triggered = alerts.filter((a) => a.triggered).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🐌 Latency Alerts</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{alerts.length} alerts</span>
          {triggered > 0 && <p className="text-[10px] text-red-500">{triggered} triggered</p>}
        </div>
      </div>
      {alerts.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No latency alerts</p>
      ) : (
        <div className="space-y-1">
          {alerts.map((a) => (
            <div key={a.alert_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-2 w-2 rounded-full ${a.triggered ? "bg-red-500" : "bg-green-500"}`} />
                <span className="truncate max-w-[140px] text-gray-700 dark:text-gray-300">{a.destination}</span>
              </div>
              <span className="text-gray-400">{a.current_avg_ms}ms / {a.threshold_ms}ms</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
