"use client";

interface ErrorBudgetWidgetProps { appId: string; consumedPct: number;
  remainingPct: number; burnRate: number; status: string; daysRemaining: number; }

export function ErrorBudgetWidget({ appId, consumedPct, remainingPct, burnRate, status, daysRemaining }: ErrorBudgetWidgetProps) {
  const barColor = status === "healthy" ? "bg-green-500" : status === "warning" ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold">🎯 Error Budget</h4>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          status === "healthy" ? "bg-green-100 text-green-700" :
          status === "warning" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
        }`}>{status}</span>
      </div>
      <div className="text-center mb-2">
        <p className="text-2xl font-bold">{remainingPct}%</p>
        <p className="text-xs text-gray-400">remaining · {daysRemaining}d left</p>
      </div>
      <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-1">
        <div className={`h-full rounded-full ${barColor}`} style={{ width: `${Math.min(consumedPct, 100)}%` }} />
      </div>
      <p className="text-xs text-gray-400 text-right">Burn rate: {burnRate}x</p>
    </div>
  );
}
