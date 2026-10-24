"use client";

interface BudgetResult { metric: string; limit: number; actual: number; over: boolean; pctOfBudget: number; }
interface PerformanceBudgetProps { results: BudgetResult[]; violations: number; withinBudget: boolean; }

export function PerformanceBudget({ results, violations, withinBudget }: PerformanceBudgetProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Performance Budget</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${withinBudget ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {withinBudget ? "✓ Within budget" : `✗ ${violations} over budget`}
        </span>
      </div>
      <div className="space-y-2">
        {results.map(r => (
          <div key={r.metric} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="font-mono text-xs">{r.metric}</span>
              <span className={`text-xs ${r.over ? "text-red-600 font-medium" : "text-gray-400"}`}>
                {r.actual} / {r.limit} ({r.pctOfBudget}%)
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${r.over ? "bg-red-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(r.pctOfBudget, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
