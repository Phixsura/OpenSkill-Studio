"use client";

interface Alert { alert_id: string; type: string; threshold: number; status: string; notify_channels: string[]; }
interface TriggeredAlert { alert_id: string; type: string; current: number; threshold: number; severity: string; exceeded_by_pct: number; }
interface BillingAlertManagerProps { alerts: Alert[]; triggered: TriggeredAlert[];
  onDelete: (id: string) => void; onCreate: () => void; }

export function BillingAlertManager({ alerts, triggered, onDelete, onCreate }: BillingAlertManagerProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Billing Alerts</h2>
        <button onClick={onCreate} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add Alert</button>
      </div>
      {triggered.length > 0 && (
        <div className="space-y-2">
          {triggered.map(t => (
            <div key={t.alert_id} className={`rounded-lg border p-3 ${t.severity === "critical" ? "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/10" : "border-yellow-300 bg-yellow-50 dark:border-yellow-700 dark:bg-yellow-900/10"}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">⚠️ {t.type.replace(/_/g, " ")}</span>
                <span className={`text-xs font-bold uppercase ${t.severity === "critical" ? "text-red-600" : "text-yellow-600"}`}>{t.severity}</span>
              </div>
              <p className="mt-1 text-xs text-gray-500">${t.current} / ${t.threshold} threshold (+{t.exceeded_by_pct}%)</p>
            </div>
          ))}
        </div>
      )}
      <div className="space-y-2">
        {alerts.map(a => (
          <div key={a.alert_id} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div>
              <span className="text-sm font-medium">{a.type.replace(/_/g, " ")}</span>
              <span className="ml-2 text-xs text-gray-400">${a.threshold}</span>
            </div>
            <button onClick={() => onDelete(a.alert_id)} className="text-xs text-red-500">Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}
