"use client";

interface ErrorBudgetGaugeProps { budgetPct: number; burnRate: number; sloTarget: number; recommendation: string; }

export function ErrorBudgetGauge({ budgetPct, burnRate, sloTarget, recommendation }: ErrorBudgetGaugeProps) {
  const color = budgetPct > 50 ? "text-green-600" : budgetPct > 20 ? "text-yellow-600" : "text-red-600";
  const bgColor = budgetPct > 50 ? "bg-green-500" : budgetPct > 20 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Error Budget</h3>
        <span className="text-xs text-gray-400">SLO: {sloTarget}%</span>
      </div>
      <div className="mt-3 text-center">
        <p className={`text-3xl font-bold ${color}`}>{budgetPct}%</p>
        <p className="text-xs text-gray-400">remaining</p>
      </div>
      <div className="mt-2 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${bgColor}`} style={{ width: `${budgetPct}%` }} />
      </div>
      <div className="mt-2 flex justify-between text-xs">
        <span>Burn rate: {burnRate}x</span>
        <span className={budgetPct <= 0 ? "text-red-600 font-bold" : ""}>{recommendation.split(":")[0]}</span>
      </div>
    </div>
  );
}
