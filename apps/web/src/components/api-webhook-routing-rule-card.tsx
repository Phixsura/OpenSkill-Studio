"use client";

interface RuleInfo { rule_id: string; event_pattern: string; destination: string; priority: number; enabled: boolean; routed_count: number; }
interface Props { rules: RuleInfo[]; appName: string; }

export default function APIWebhookRoutingRuleCard({ rules, appName }: Props) {
  const enabled = rules.filter((r) => r.enabled).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔀 Routing Rules</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{enabled}/{rules.length} active</span>
      </div>
      {rules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No routing rules</p>
      ) : (
        <div className="space-y-1">
          {rules.map((r) => (
            <div key={r.rule_id} className={`flex items-center justify-between text-[11px] ${!r.enabled ? "opacity-50" : ""}`}>
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-gray-700 dark:text-gray-300">{r.event_pattern}</span>
                <span className="text-gray-400">→</span>
                <span className="truncate max-w-[120px] text-gray-500">{r.destination}</span>
              </div>
              <span className="text-gray-400">P{r.priority} · {r.routed_count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
