"use client";

interface BudgetResult { metric: string; limit: number; actual: number;
  over: boolean; pctOfBudget: number; }
interface PerfBudgetCardProps { name: string; results: BudgetResult[];
  violations: number; withinBudget: boolean; trend: string; }

export function PerfBudgetCard({ name, results, violations, withinBudget, trend }: PerfBudgetCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">⚡ {name}</h3>
        <div className="flex gap-2 text-xs">
          <span className={withinBudget ? "text-green-600" : "text-red-500"}>
            {withinBudget ? "✅ Within Budget" : `⚠ ${violations} over`}
          </span>
          <span className="text-gray-400">{trend}</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {results.map(r => (
          <div key={r.metric} className="px-4 py-2.5">
            <div className="flex items-center justify-between mb-1 text-xs">
              <span className="font-mono">{r.metric}</span>
              <span className={r.over ? "text-red-600 font-bold" : "text-green-600"}>
                {r.actual} / {r.limit}
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${r.over ? "bg-red-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(r.pctOfBudget, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
