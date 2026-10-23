"use client";

interface ErrorBudgetGaugeProps { sloTarget: number; actualSuccessRate: number; budgetPctUsed: number;
  budgetRemaining: number; status: string; estimatedDaysRemaining: number; }

export function ErrorBudgetGauge({ sloTarget, actualSuccessRate, budgetPctUsed, budgetRemaining, status, estimatedDaysRemaining }: ErrorBudgetGaugeProps) {
  const color = status === "ok" ? "text-green-600" : status === "warning" ? "text-yellow-600" : "text-red-600";
  const barColor = status === "ok" ? "bg-green-500" : status === "warning" ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Error Budget</h2>
        <span className={`text-sm font-bold uppercase ${color}`}>{status}</span>
      </div>
      <div className="text-center">
        <p className="text-3xl font-bold">{actualSuccessRate}%</p>
        <p className="text-xs text-gray-400">Actual vs {sloTarget}% SLO target</p>
      </div>
      <div>
        <div className="flex justify-between text-xs text-gray-400">
          <span>Budget Used</span><span>{budgetPctUsed}%</span>
        </div>
        <div className="mt-1 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(budgetPctUsed, 100)}%` }} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3 text-center text-sm">
        <div>
          <p className="font-bold">{budgetRemaining.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Errors Remaining</p>
        </div>
        <div>
          <p className="font-bold">{estimatedDaysRemaining < 999 ? `${estimatedDaysRemaining}d` : "∞"}</p>
          <p className="text-xs text-gray-400">Days Left</p>
        </div>
      </div>
    </div>
  );
}
