"use client";

interface BudgetInfo { consumer_id: string; budget_per_minute: number; used: number; remaining: number; usage_pct: number; total_exhausted: number; }
interface Props { budgets: BudgetInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudgetCard({ budgets, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Retry Budgets</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {budgets.length} consumers</p>
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry budgets</p>
      ) : (
        <div className="space-y-1.5">
          {budgets.map((b) => (
            <div key={b.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{b.consumer_id}</span>
                <span className="text-gray-400">{b.used}/{b.budget_per_minute}/min</span>
              </div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1 rounded-full ${b.usage_pct >= 90 ? "bg-red-500" : "bg-blue-500"}`} style={{ width: `${Math.min(b.usage_pct, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
