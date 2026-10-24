"use client";

interface PolicyTrigger { policy: string; threshold: number; action: string; severity: string; }
interface ErrBudgetPolPanelProps { budgetPct: number; triggered: PolicyTrigger[];
  recommendedAction: string; freezeDeploys: boolean; daysToExhaustion: number; }

export function ErrBudgetPolPanel({ budgetPct, triggered, recommendedAction, freezeDeploys, daysToExhaustion }: ErrBudgetPolPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📊 Error Budget Policy</h3>
        <span className={`text-xs font-bold ${freezeDeploys ? "text-red-600" : budgetPct > 80 ? "text-yellow-600" : "text-green-600"}`}>
          {budgetPct}% consumed · {freezeDeploys ? "🛑 FROZEN" : `${daysToExhaustion}d left`}
        </span>
      </div>
      <div className="p-4">
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full mb-2">
          <div className={`h-full rounded-full ${budgetPct >= 100 ? "bg-red-500" : budgetPct >= 80 ? "bg-yellow-500" : "bg-green-500"}`}
            style={{ width: `${Math.min(budgetPct, 100)}%` }} />
        </div>
        {recommendedAction !== "none" && (
          <div className="text-xs text-gray-400">Action: <span className="font-bold">{recommendedAction.replace(/_/g, " ")}</span></div>
        )}
      </div>
      {triggered.length > 0 && (
        <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
          {triggered.map(t => (
            <div key={t.policy} className="flex justify-between px-4 py-1.5 text-xs">
              <span>{t.policy} ({t.threshold}%)</span>
              <span className={t.severity === "critical" ? "text-red-500" : "text-yellow-600"}>{t.severity}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
