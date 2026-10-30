"use client";

interface BudgetInfo { consumer_id: string; period: string; allocated: number; used: number; remaining: number; usage_pct: number; rollover: number; }
interface Props { budgets: BudgetInfo[]; nearExhaustionCount: number; appName: string; }

const barColor = (pct: number) => pct >= 95 ? "bg-red-500" : pct >= 80 ? "bg-yellow-500" : "bg-green-500";

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudgetCard({ budgets, nearExhaustionCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💳 Request Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {nearExhaustionCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {nearExhaustionCount} near limit</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={`${b.consumer_id}-${b.period}`} className="text-[11px]">
              <div className="flex justify-between"><span className="text-gray-700 dark:text-gray-300">{b.consumer_id}</span><span className="text-gray-400">{b.used.toLocaleString()}/{(b.allocated + b.rollover).toLocaleString()}</span></div>
              <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800"><div className={`h-1 rounded-full ${barColor(b.usage_pct)}`} style={{ width: `${Math.min(b.usage_pct, 100)}%` }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
