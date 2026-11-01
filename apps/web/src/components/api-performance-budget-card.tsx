"use client";

interface BudgetInfo {
  budget_id: string;
  metric: string;
  max_value: number;
  current_value: number;
  usage_pct: number;
  within_budget: boolean;
  violations: number;
}

interface APIPerformanceBudgetCardProps {
  budgets: BudgetInfo[];
  appName: string;
}

export default function APIPerformanceBudgetCard({ budgets, appName }: APIPerformanceBudgetCardProps) {
  const violating = budgets.filter((b) => !b.within_budget).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⚡ Perf Budgets</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{budgets.length} budgets</span>
          {violating > 0 && <p className="text-[10px] text-red-500">{violating} over budget</p>}
        </div>
      </div>

      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No performance budgets</p>
      ) : (
        <div className="space-y-2">
          {budgets.map((b) => {
            const barColor = !b.within_budget ? "bg-red-500" : b.usage_pct >= 80 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={b.budget_id}>
                <div className="flex justify-between text-[11px]">
                  <span className="text-gray-700 dark:text-gray-300">{b.metric}</span>
                  <span className="text-gray-400">{b.current_value} / {b.max_value}</span>
                </div>
                <div className="mt-0.5 h-1 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div className={`h-1 rounded-full ${barColor}`} style={{ width: `${Math.min(100, b.usage_pct)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
