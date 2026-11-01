"use client";

interface ErrBudgetCardProps { sloTarget: number; budgetTotal: number; budgetConsumed: number;
  budgetRemaining: number; pctConsumed: number; status: string; trend: string; }

const STATUS_STYLE: Record<string, string> = { ok: "text-green-600", warning: "text-yellow-600", exhausted: "text-red-600" };

export function ErrBudgetCard({ sloTarget, budgetTotal, budgetConsumed, budgetRemaining, pctConsumed, status, trend }: ErrBudgetCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💰 Error Budget</h3>
        <span className={`text-xs font-bold ${STATUS_STYLE[status] ?? ""}`}>
          {status} · SLO {(sloTarget * 100).toFixed(1)}%
        </span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">{pctConsumed}% consumed</span>
          <span className="text-gray-400">{budgetRemaining.toLocaleString()} remaining</span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${status === "exhausted" ? "bg-red-500" : status === "warning" ? "bg-yellow-500" : "bg-green-500"}`}
            style={{ width: `${Math.min(pctConsumed, 100)}%` }} />
        </div>
        <div className="text-xs text-gray-400 mt-2 text-center">
          {budgetConsumed.toLocaleString()} / {budgetTotal.toLocaleString()} errors · trend: {trend}
        </div>
      </div>
    </div>
  );
}
