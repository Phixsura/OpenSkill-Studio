"use client";

interface Budget { name: string; target: number; actual: number;
  consumedPct: number; remainingPct: number; exhausted: boolean; }
interface ErrBudgetDashboardProps { budgets: Budget[]; totalSlos: number;
  exhausted: number; avgRemainingPct: number; status: string; }

export function ErrBudgetDashboard({ budgets, totalSlos, exhausted, avgRemainingPct, status }: ErrBudgetDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎯 Error Budgets</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{totalSlos} SLOs · avg {avgRemainingPct}% remaining</span>
          {exhausted > 0 && <span className="text-red-500">⚠ {exhausted} exhausted</span>}
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {budgets.map(b => (
          <div key={b.name} className="px-4 py-2.5">
            <div className="flex justify-between text-xs mb-0.5">
              <span className={b.exhausted ? "text-red-600 font-bold" : ""}>{b.name}</span>
              <span className="text-gray-400">{b.actual}% / {b.target}% · {b.remainingPct}% budget left</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${b.exhausted ? "bg-red-500" : b.consumedPct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(b.consumedPct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
