"use client";

interface BudgetInfo { endpoint: string; max_latency_ms: number; actual_latency_ms: number; max_response_bytes: number; actual_response_bytes: number; within_budget: boolean; violation_count: number; }
interface Props { budgets: BudgetInfo[]; violationCount: number; appName: string; }

function fmtSize(b: number) { return b < 1024 ? `${b}B` : `${(b/1024).toFixed(1)}KB`; }

export default function APIDeveloperAPIApiPerformanceBudgetCard({ budgets, violationCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Performance Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {violationCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] text-red-700">{violationCount} over budget</span>}
      </div>
      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No performance budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => (
            <div key={b.endpoint} className={`rounded-lg p-2 ${b.within_budget ? "bg-green-50 dark:bg-green-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
              <div className="flex items-center justify-between text-[11px]">
                <span className="font-medium text-gray-700 dark:text-gray-300">{b.endpoint}</span>
                <span className={b.within_budget ? "text-green-600" : "text-red-500 font-bold"}>{b.within_budget ? "✓" : "✗"}</span>
              </div>
              <div className="mt-0.5 flex gap-3 text-[10px] text-gray-400">
                <span>latency: {b.actual_latency_ms}/{b.max_latency_ms}ms</span>
                <span>size: {fmtSize(b.actual_response_bytes)}/{fmtSize(b.max_response_bytes)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
