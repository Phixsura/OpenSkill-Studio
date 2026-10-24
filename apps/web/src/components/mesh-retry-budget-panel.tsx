"use client";
interface RetryBudgetInfo { key: string; budget: number; used: number; usedPct: number; exhausted: boolean; }
interface MeshRetryBudgetPanelProps { budgets: RetryBudgetInfo[]; budgetPct: number; }
export function MeshRetryBudgetPanel({ budgets, budgetPct }: MeshRetryBudgetPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Retry Budgets</h3>
        <span className="text-xs text-gray-400">{budgetPct}% budget · {budgets.length} pairs</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {budgets.map(b => (
          <div key={b.key} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{b.key}</span>
              <span className={b.exhausted ? "text-red-500 font-bold" : "text-gray-400"}>
                {b.used}/{b.budget} ({b.usedPct}%){b.exhausted ? " EXHAUSTED" : ""}
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${b.exhausted ? "bg-red-500" : b.usedPct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(b.usedPct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
