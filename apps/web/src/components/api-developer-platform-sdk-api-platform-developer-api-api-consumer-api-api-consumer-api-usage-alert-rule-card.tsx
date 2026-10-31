"use client";

interface RuleInfo { rule_id: string; consumer_id: string; metric: string; condition: string; threshold: number; severity: string; fired_count: number; }
interface Props { rules: RuleInfo[]; appName: string; }

const sevColor: Record<string, string> = { info: "text-blue-600 dark:text-blue-400", warning: "text-yellow-600 dark:text-yellow-400", critical: "text-red-600 dark:text-red-400" };
const condLabel: Record<string, string> = { gt: ">", lt: "<", gte: "≥", lte: "≤" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRuleCard({ rules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔔 Alert Rules</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {rules.length} rules</p>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No alert rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{r.metric} {condLabel[r.condition] ?? r.condition} {r.threshold}</span>
              <span className={sevColor[r.severity] ?? "text-gray-400"}>{r.severity} · {r.fired_count}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
