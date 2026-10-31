"use client";

interface BudgetInfo { endpoint: string; budget_ms: number; p99_ms: number; within_budget: boolean; headroom_pct: number; violation_rate: number; }
interface Props { budgets: BudgetInfo[]; overBudgetCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiEndpointResponseTimeBudgetCard({ budgets, overBudgetCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Response Time Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {overBudgetCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{overBudgetCount} over budget</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No time budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={b.endpoint} className={`rounded-lg p-2 ${b.within_budget ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{b.endpoint}</span>
                <span className={b.within_budget ? "text-green-600" : "text-red-500 font-bold"}>p99: {b.p99_ms}ms / {b.budget_ms}ms</span>
              </div>
              <p className="mt-0.5 text-[10px] text-gray-400">headroom: {b.headroom_pct}% · violations: {b.violation_rate}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
