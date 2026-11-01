"use client";
interface BudgetStage { stage: string; budgetMs: number; pct: number; }
interface LatencyBudgetPanelProps { totalMs: number; stages: BudgetStage[]; remainingMs: number; }
export function LatencyBudgetPanel({ totalMs, stages, remainingMs }: LatencyBudgetPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏱️ Latency Budget</h3>
        <span className="text-xs text-gray-400">{totalMs}ms total · {remainingMs}ms remaining</span>
      </div>
      <div className="p-4">
        <div className="flex h-4 rounded-full overflow-hidden mb-2">
          {stages.map((s, i) => (
            <div key={s.stage} className={`${i === 0 ? "bg-blue-500" : i === 1 ? "bg-green-500" : i === 2 ? "bg-yellow-500" : "bg-purple-500"}`}
              style={{ width: `${s.pct}%` }} title={`${s.stage}: ${s.budgetMs}ms`} />
          ))}
          {remainingMs > 0 && <div className="bg-gray-200 dark:bg-gray-700" style={{ width: `${remainingMs / totalMs * 100}%` }} />}
        </div>
        <div className="flex flex-wrap gap-2 text-[10px]">
          {stages.map(s => <span key={s.stage} className="text-gray-400">{s.stage}: {s.budgetMs}ms ({s.pct}%)</span>)}
        </div>
      </div>
    </div>
  );
}
