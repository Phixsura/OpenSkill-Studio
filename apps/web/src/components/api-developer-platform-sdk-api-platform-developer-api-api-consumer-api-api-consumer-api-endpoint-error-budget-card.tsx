"use client";

interface BudgetInfo { consumer_id: string; endpoint: string; method: string; slo_pct: number; budget_used_pct: number; status: string; }
interface Props { budgets: BudgetInfo[]; atRiskCount: number; appName: string; }

const statusColor: Record<string, string> = { healthy: "text-green-600 dark:text-green-400", warning: "text-yellow-600 dark:text-yellow-400", critical: "text-orange-600 dark:text-orange-400", exhausted: "text-red-600 dark:text-red-400" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudgetCard({ budgets, atRiskCount, appName }: Props) {
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
        <div className="space-y-1">
          {budgets.map((b) => (
            <div key={`${b.consumer_id}-${b.method}-${b.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{b.consumer_id} · {b.method} {b.endpoint}</span>
              <span className={statusColor[b.status]}>{b.budget_used_pct}% used</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
