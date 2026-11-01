"use client";

interface BudgetInfo { destination: string; max_retries_per_hour: number; retries_used: number; remaining: number; usage_pct: number; exhausted: boolean; }
interface Props { budgets: BudgetInfo[]; exhaustedCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiWebhookRetryBudgetCard({ budgets, exhaustedCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Retry Budget</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {exhaustedCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{exhaustedCount} exhausted</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No retry budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={b.destination}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(b.destination).hostname}</span>
                <span className={b.exhausted ? "text-red-500 font-bold" : "text-gray-400"}>{b.remaining}/{b.max_retries_per_hour} remaining</span>
              </div>
              <div className="mt-0.5 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                <div className={`h-1.5 rounded-full ${b.usage_pct >= 90 ? "bg-red-500" : b.usage_pct >= 70 ? "bg-yellow-500" : "bg-green-500"}`} style={{ width: `${b.usage_pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
