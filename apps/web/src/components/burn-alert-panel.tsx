"use client";
interface BurnAlert { window: string; burnRate: number; threshold: number; severity: string; }
interface BurnAlertPanelProps { firing: boolean; alerts: BurnAlert[]; currentBurnRate: number; mostSevere: string; }
const SEV_COLOR: Record<string, string> = { critical: "text-red-600", warning: "text-yellow-600", info: "text-blue-500" };
export function BurnAlertPanel({ firing, alerts, currentBurnRate, mostSevere }: BurnAlertPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔥 Burn Alert</h3>
        <span className={`text-xs font-bold ${firing ? SEV_COLOR[mostSevere] ?? "text-red-500" : "text-green-600"}`}>
          {firing ? `🚨 ${mostSevere.toUpperCase()} · ${currentBurnRate}x` : "✅ OK"}
        </span>
      </div>
      {alerts.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {alerts.map(a => (
            <div key={a.window} className="flex justify-between px-4 py-1.5 text-xs">
              <span>{a.window}</span>
              <span className={SEV_COLOR[a.severity] ?? ""}>{a.burnRate}x (threshold: {a.threshold}x)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
