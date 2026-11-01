"use client";

interface BudgetInfo { endpoint: string; slo_target_pct: number; budget_consumed_pct: number; budget_remaining: number; status: string; }
interface Props { budgets: BudgetInfo[]; alertCount: number; appName: string; }

const statusStyle: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", warning: "text-yellow-600 dark:text-yellow-400", critical: "text-orange-600 dark:text-orange-400", exhausted: "text-red-600 dark:text-red-400" };
const statusEmoji: Record<string, string> = { healthy: "✅", warning: "⚠️", critical: "🔶", exhausted: "🔴" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudgetCard({ budgets, alertCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Error Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {budgets.length} endpoints</p>
        </div>
        {alertCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">{alertCount} alerts</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={b.endpoint} className="text-[11px]">
              <div className="flex justify-between">
                <span className="text-gray-700 dark:text-gray-300">{b.endpoint} <span className="text-gray-400">({b.slo_target_pct}%)</span></span>
                <span className={statusStyle[b.status] ?? "text-gray-400"}>{statusEmoji[b.status] ?? ""} {b.status}</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1 rounded-full ${b.budget_consumed_pct >= 80 ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${Math.min(b.budget_consumed_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
