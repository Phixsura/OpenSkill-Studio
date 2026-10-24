"use client";

interface AlertInfo { rule: string; metric: string; value: number; threshold: number; severity: string; }
interface AlertRulePanelProps { alerts: AlertInfo[]; hasCritical: boolean; total: number; }

const SEV_STYLE: Record<string, string> = { critical: "text-red-600", warning: "text-yellow-600", info: "text-blue-500" };

export function AlertRulePanel({ alerts, hasCritical, total }: AlertRulePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔔 Alert Rules</h3>
        <span className={`text-xs font-bold ${hasCritical ? "text-red-500" : total > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {total > 0 ? `${total} firing` : "✅ Clear"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {alerts.map((a, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div>
              <span className={`font-bold ${SEV_STYLE[a.severity] ?? ""}`}>{a.rule}</span>
              <span className="text-gray-400 ml-2">{a.metric}: {a.value} (threshold: {a.threshold})</span>
            </div>
            <span className={SEV_STYLE[a.severity] ?? ""}>{a.severity}</span>
          </div>
        ))}
        {alerts.length === 0 && <div className="px-4 py-3 text-xs text-gray-400 text-center">No alerts firing</div>}
      </div>
    </div>
  );
}
