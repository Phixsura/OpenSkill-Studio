"use client";
interface Stage { name: string; ms: number; pct: number; }
interface RtBudgetPanelProps { endpoint: string; budgetMs: number; usedMs: number;
  remainingMs: number; pctUsed: number; overBudget: boolean; stages: Stage[]; }
export function RtBudgetPanel({ endpoint, budgetMs, usedMs, remainingMs, pctUsed, overBudget, stages }: RtBudgetPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ RT Budget: {endpoint}</h3>
        <span className={`text-xs font-bold ${overBudget ? "text-red-500" : "text-green-600"}`}>
          {usedMs}/{budgetMs}ms ({pctUsed}%){overBudget ? " ⚠ OVER" : ` · ${remainingMs}ms left`}
        </span>
      </div>
      <div className="p-4">
        <div className="flex h-4 rounded-full overflow-hidden mb-2">
          {stages.map(s => (
            <div key={s.name} className="bg-blue-500 border-r border-white dark:border-gray-800"
              style={{ width: `${s.pct}%` }} title={`${s.name}: ${s.ms}ms`} />
          ))}
          {!overBudget && <div className="bg-gray-200 dark:bg-gray-700 flex-1" />}
        </div>
        <div className="flex flex-wrap gap-2 text-[10px]">
          {stages.map(s => <span key={s.name} className="text-gray-400">{s.name}: {s.ms}ms</span>)}
        </div>
      </div>
    </div>
  );
}
