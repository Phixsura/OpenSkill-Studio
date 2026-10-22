"use client";

interface Violation { metric: string; actual: number; limit: number; unit: string; }
interface PerformanceBudgetCardProps { withinBudget: boolean; score: number; violations: Violation[]; }

export function PerformanceBudgetCard({ withinBudget, score, violations }: PerformanceBudgetCardProps) {
  return (
    <div className={`rounded-lg border p-4 ${withinBudget ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Performance Budget</h3>
        <span className={`text-lg font-bold ${score === 100 ? "text-green-600" : "text-red-600"}`}>{score}%</span>
      </div>
      {withinBudget ? (
        <p className="mt-2 text-sm text-green-600">✅ All metrics within budget</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {violations.map(v => (
            <li key={v.metric} className="flex justify-between text-sm text-red-600">
              <span>❌ {v.metric.replace("_", " ")}</span>
              <span>{v.actual}{v.unit} / {v.limit}{v.unit}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
