"use client";

interface RetryPolicyPanelProps { strategy: string; maxAttempts: number; baseMs: number;
  budgetUsed: number; budgetTotal: number; budgetPct: number; exhausted: boolean; }

export function RetryPolicyPanel({ strategy, maxAttempts, baseMs, budgetUsed, budgetTotal, budgetPct, exhausted }: RetryPolicyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Retry Policy</h3>
        <span className={`text-xs ${exhausted ? "text-red-500" : "text-green-600"}`}>
          {strategy} · max {maxAttempts} · {baseMs}ms base
        </span>
      </div>
      <div className="p-4">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-400">Retry Budget</span>
          <span className="text-gray-400">{budgetUsed}/{budgetTotal} ({budgetPct}%)</span>
        </div>
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${exhausted ? "bg-red-500" : budgetPct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
            style={{ width: `${Math.min(budgetPct, 100)}%` }} />
        </div>
      </div>
    </div>
  );
}
