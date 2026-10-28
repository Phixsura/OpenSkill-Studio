"use client";

interface ErrorBudgetInfo {
  service_id: string;
  slo_target: number;
  budget_total: number;
  error_count: number;
  budget_remaining: number;
  budget_consumed_pct: number;
  is_exhausted: boolean;
}

interface ErrorBudgetCardProps {
  budgets: ErrorBudgetInfo[];
  appName: string;
}

export default function ErrorBudgetCard({ budgets, appName }: ErrorBudgetCardProps) {
  const exhausted = budgets.filter((b) => b.is_exhausted).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🎯 Error Budgets
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{budgets.length} services</span>
          {exhausted > 0 && (
            <p className="text-[10px] font-medium text-red-600 dark:text-red-400">
              {exhausted} exhausted
            </p>
          )}
        </div>
      </div>

      {budgets.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error budgets</p>
      ) : (
        <div className="space-y-3">
          {budgets.map((b) => {
            const barColor = b.is_exhausted
              ? "bg-red-500"
              : b.budget_consumed_pct >= 80
                ? "bg-yellow-500"
                : "bg-green-500";
            return (
              <div key={b.service_id}>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {b.service_id}
                  </span>
                  <span className="text-gray-400">SLO {b.slo_target}%</span>
                </div>
                <div className="mt-1 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                  <div
                    className={`h-1.5 rounded-full ${barColor}`}
                    style={{ width: `${Math.min(100, b.budget_consumed_pct)}%` }}
                  />
                </div>
                <div className="mt-0.5 flex justify-between text-[10px] text-gray-400">
                  <span>{b.budget_consumed_pct}% consumed</span>
                  <span>{b.budget_remaining} remaining</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
