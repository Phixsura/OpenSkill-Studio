"use client";

interface AlertRule { name: string; metric: string; operator: string; threshold: number;
  status: string; channel: string; severity: string; }
interface AlertRulesPanelProps { rules: AlertRule[]; firing: number; healthy: boolean; }

const sevColors: Record<string, string> = {
  critical: "text-red-600", warning: "text-yellow-600", info: "text-blue-600",
};

export function AlertRulesPanel({ rules, firing, healthy }: AlertRulesPanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Alert Rules</h3>
        <div className="flex items-center gap-1.5">
          <span className={`h-2 w-2 rounded-full ${healthy ? "bg-green-500" : "bg-red-500 animate-pulse"}`} />
          <span className="text-xs text-gray-400">{healthy ? "All clear" : `${firing} firing`}</span>
        </div>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {rules.map((r, i) => (
          <div key={i} className={`flex items-center justify-between px-4 py-2.5 ${r.status === "firing" ? "bg-red-50 dark:bg-red-900/10" : ""}`}>
            <div>
              <p className="text-sm font-medium">{r.name}</p>
              <p className="text-xs text-gray-400">{r.metric} {r.operator} {r.threshold}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`text-xs ${sevColors[r.severity] ?? ""}`}>{r.severity}</span>
              <span className={`rounded px-1.5 py-0.5 text-xs ${r.status === "firing" ? "bg-red-100 text-red-700 dark:bg-red-900/30" : "bg-green-100 text-green-700 dark:bg-green-900/30"}`}>
                {r.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
