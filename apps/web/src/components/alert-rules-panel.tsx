"use client";

interface AlertRule { name: string; metric: string; operator: string; threshold: number; triggered: boolean; }
interface AlertRulesPanelProps { rules: AlertRule[]; activeCount: number; }

const OP_LABELS: Record<string, string> = { gt: ">", lt: "<", gte: "≥", lte: "≤", eq: "=" };

export function AlertRulesPanel({ rules, activeCount }: AlertRulesPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Alert Rules</h3>
        {activeCount > 0 && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
            {activeCount} active
          </span>
        )}
      </div>
      {rules.length === 0 ? <p className="mt-2 text-sm text-gray-400">No alert rules.</p> : (
        <ul className="mt-3 space-y-2">
          {rules.map(r => (
            <li key={r.name} className={`flex items-center justify-between rounded border p-2 text-sm ${r.triggered ? "border-red-300 bg-red-50 dark:border-red-700 dark:bg-red-900/20" : "dark:border-gray-700"}`}>
              <div>
                <span className="font-medium">{r.name}</span>
                <span className="ml-2 text-xs text-gray-400">{r.metric} {OP_LABELS[r.operator] || r.operator} {r.threshold}</span>
              </div>
              <span>{r.triggered ? "🔴" : "🟢"}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
