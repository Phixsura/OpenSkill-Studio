"use client";

interface RuleInfo { rule_id: string; event_type: string; action: string; field_count: number; }
interface Props { consumerId: string; rules: RuleInfo[]; totalRules: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRuleCard({ consumerId, rules, totalRules, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔍 Webhook Filters</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalRules} rules</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No filter rules (all events delivered)</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={r.action === "include" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}>{r.action === "include" ? "✅" : "🚫"}</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">{r.event_type}</span>
              </div>
              {r.field_count > 0 && <span className="text-gray-400">+{r.field_count} fields</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
