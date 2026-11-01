"use client";

interface BudgetInfo { consumer_id: string; slo_pct: number; budget_remaining_pct: number; burn_rate: number; exhausted: boolean; current_success_pct: number; }
interface Props { budgets: BudgetInfo[]; exhaustedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudgetCard({ budgets, exhaustedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Consumer Error Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exhaustedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{exhaustedCount} exhausted</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.slice(0, 5).map((b) => (
            <div key={b.consumer_id} className={`rounded-lg p-2 ${b.exhausted ? "bg-red-50 dark:bg-red-900/20" : "bg-gray-50 dark:bg-gray-800"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{b.consumer_id}</span>
                <span className={b.exhausted ? "text-red-500 font-bold" : "text-green-600"}>{b.budget_remaining_pct}% remaining</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>SLO: {b.slo_pct}%</span>
                <span>actual: {b.current_success_pct}%</span>
                <span>burn: {b.burn_rate}x</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
