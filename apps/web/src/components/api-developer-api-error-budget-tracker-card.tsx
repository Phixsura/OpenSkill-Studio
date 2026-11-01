"use client";

interface BudgetInfo { endpoint: string; slo_target_pct: number; current_success_pct: number; budget_remaining_pct: number; budget_exhausted: boolean; }
interface Props { budgets: BudgetInfo[]; appName: string; }

export default function APIDeveloperAPIErrorBudgetTrackerCard({ budgets, appName }: Props) {
  const exhaustedCount = budgets.filter(b => b.budget_exhausted).length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🎯 Error Budget Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exhaustedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700">{exhaustedCount} exhausted</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error budgets configured</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={b.endpoint} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{b.endpoint}</span>
                <span className={b.budget_exhausted ? "text-red-500 font-bold" : "text-green-600"}>{b.budget_remaining_pct}% remaining</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[10px] text-gray-400">
                <span>SLO: {b.slo_target_pct}%</span>
                <span>Current: {b.current_success_pct}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
