"use client";

interface Condition { metric: string; operator: string; threshold: number; }
interface Rule { id: string; name: string; severity: string; conditions: Condition[]; enabled: boolean; }
interface Alert { ruleId: string; ruleName: string; severity: string; conditionsMet: string[]; timestamp: string; }
interface Props { rules: Rule[]; recentAlerts: Alert[]; appName: string; }

const sevColors: Record<string, string> = { info: "bg-blue-100 text-blue-700", warning: "bg-amber-100 text-amber-700", critical: "bg-red-100 text-red-700" };

export default function APIDeveloperPlatformSDKConsumerApiAlertRuleEngineCard({ rules, recentAlerts, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Alert Rules</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules · {recentAlerts.length} recent alerts</p>
      </div>
      {recentAlerts.length > 0 && (
        <div className="mb-3 space-y-1">
          {recentAlerts.slice(0, 3).map((a, i) => (
            <div key={i} className={`rounded p-1.5 text-[10px] ${sevColors[a.severity] ?? ""}`}>🚨 {a.ruleName}: {a.conditionsMet.join(", ")}</div>
          ))}
        </div>
      )}
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No alert rules</p>
      ) : (
        <div className="space-y-0.5">
          {rules.map((r) => (
            <div key={r.id} className={`flex items-center justify-between text-[10px] ${!r.enabled ? "opacity-50" : ""}`}>
              <span className="text-gray-700 dark:text-gray-300">{r.name} ({r.conditions.length} conditions)</span>
              <span className={`rounded px-1 py-0.5 text-[9px] ${sevColors[r.severity] ?? ""}`}>{r.severity}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
