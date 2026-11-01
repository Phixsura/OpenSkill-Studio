"use client";
interface CapAlert { service: string; severity: string; bottleneck: string; utilization: number; }
interface CapacityAlertPanelProps { alerts: CapAlert[]; critical: number; servicesChecked: number; }
const SEV_COLOR: Record<string, string> = { critical: "text-red-600", warning: "text-yellow-600" };
export function CapacityAlertPanel({ alerts, critical, servicesChecked }: CapacityAlertPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚠️ Capacity Alerts</h3>
        <span className={`text-xs font-bold ${alerts.length > 0 ? "text-red-500" : "text-green-600"}`}>
          {alerts.length > 0 ? `${alerts.length} alerts (${critical} critical)` : "✅ All OK"} · {servicesChecked} checked
        </span>
      </div>
      {alerts.length > 0 ? (
        <div className="divide-y dark:divide-gray-700">
          {alerts.map(a => (
            <div key={a.service} className="flex justify-between px-4 py-1.5 text-xs">
              <span className={`font-mono font-bold ${SEV_COLOR[a.severity] ?? ""}`}>{a.service}</span>
              <span className="text-gray-400">{a.bottleneck} at {a.utilization}% · {a.severity}</span>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-xs text-green-600 text-center">No capacity concerns</div>
      )}
    </div>
  );
}
