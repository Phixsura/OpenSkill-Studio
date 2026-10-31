"use client";

interface BudgetInfo { consumer_id: string; endpoint: string; method: string; budget_ms: number; compliance_pct: number; meeting: boolean; }
interface Props { budgets: BudgetInfo[]; violationCount: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudgetCard({ budgets, violationCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏱️ Latency Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {violationCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">⚠️ {violationCount} violations</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No latency budgets</p>
      ) : (
        <div className="space-y-1">
          {budgets.map((b) => (
            <div key={`${b.consumer_id}-${b.method}-${b.endpoint}`} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{b.meeting ? "✅" : "❌"} {b.consumer_id} · {b.method} {b.endpoint}</span>
              <span className="text-gray-400">{b.budget_ms}ms · {b.compliance_pct}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
