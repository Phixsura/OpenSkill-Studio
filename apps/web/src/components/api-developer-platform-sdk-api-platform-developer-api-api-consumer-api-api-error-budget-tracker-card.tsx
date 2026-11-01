"use client";

interface BudgetInfo { consumer_id: string; slo_target_pct: number; budget_consumed: number; budget_remaining_pct: number; status: string; }
interface Props { budgets: BudgetInfo[]; atRiskCount: number; appName: string; }

const statusColor: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", warning: "text-yellow-600 dark:text-yellow-400", critical: "text-orange-600 dark:text-orange-400", exhausted: "text-red-600 dark:text-red-400" };
const barColor = (s: string) => s === "exhausted" ? "bg-red-500" : s === "critical" ? "bg-orange-500" : s === "warning" ? "bg-yellow-500" : "bg-green-500";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTrackerCard({ budgets, atRiskCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Error Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {atRiskCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {atRiskCount} at risk</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={b.consumer_id} className="text-[11px]">
              <div className="flex justify-between"><span className="text-gray-700 dark:text-gray-300">{b.consumer_id} ({b.slo_target_pct}%)</span><span className={statusColor[b.status]}>{b.status} · {b.budget_remaining_pct}% left</span></div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800"><div className={`h-1 rounded-full ${barColor(b.status)}`} style={{ width: `${Math.min(b.budget_consumed, 100)}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
