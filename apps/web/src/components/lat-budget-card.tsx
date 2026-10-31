"use client";

interface Stage { stage: string; budgetMs: number; actualMs: number; withinBudget: boolean; }
interface LatBudgetCardProps { endpoint: string; totalBudgetMs: number;
  allocatedMs: number; stages: Stage[]; overBudget: boolean; }

export function LatBudgetCard({ endpoint, totalBudgetMs, allocatedMs, stages, overBudget }: LatBudgetCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">⏱️ Latency Budget: {endpoint}</h3>
        <span className={`text-xs ${overBudget ? "text-red-500" : "text-green-600"}`}>
          {overBudget ? "⚠ Over Budget" : "✅ Within Budget"} · {allocatedMs}/{totalBudgetMs}ms
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {stages.map(s => (
          <div key={s.stage} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <span className={!s.withinBudget ? "text-red-600 font-bold" : ""}>{s.stage}</span>
            <span className="font-mono">{s.actualMs}ms / {s.budgetMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
