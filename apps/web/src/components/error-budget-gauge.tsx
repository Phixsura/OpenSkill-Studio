"use client";

interface ErrorBudgetGaugeProps { sloDisplay: string; consumedPct: number;
  remainingPct: number; burnRateDisplay: string; status: string; budgetTotal: number; budgetConsumed: number; }

export function ErrorBudgetGauge({ sloDisplay, consumedPct, remainingPct, burnRateDisplay, status, budgetTotal, budgetConsumed }: ErrorBudgetGaugeProps) {
  const barColor = status === "exhausted" ? "bg-red-600" : status === "critical" ? "bg-red-500" :
                   status === "warning" ? "bg-yellow-500" : "bg-green-500";
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🎯 Error Budget</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
          status === "healthy" ? "bg-green-100 text-green-700" :
          status === "warning" ? "bg-yellow-100 text-yellow-700" :
          "bg-red-100 text-red-700"
        }`}>{status}</span>
      </div>
      <div className="text-center mb-4">
        <p className="text-3xl font-bold">{remainingPct}%</p>
        <p className="text-xs text-gray-400">remaining · SLO {sloDisplay}</p>
      </div>
      <div className="h-4 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-3">
        <div className={`h-full rounded-full ${barColor} transition-all`}
             style={{ width: `${Math.min(consumedPct, 100)}%` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>{budgetConsumed.toLocaleString()} / {budgetTotal.toLocaleString()} errors</span>
        <span>Burn rate: {burnRateDisplay}</span>
      </div>
    </div>
  );
}
