"use client";

interface TimeoutCalculatorProps { chainP99Ms: number; safetyMarginMs: number;
  recommendedTimeoutMs: number; currentBudgetMs: number; overBudget: boolean;
  depsInChain: number; }

export function TimeoutCalculator({ chainP99Ms, safetyMarginMs, recommendedTimeoutMs, currentBudgetMs, overBudget, depsInChain }: TimeoutCalculatorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⏰ Timeout Calculator</h3>
        <span className={`text-xs ${overBudget ? "text-red-500" : "text-green-600"}`}>
          {overBudget ? "⚠ Over budget" : "✅ Within budget"} · {depsInChain} deps
        </span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Chain P99", v: `${chainP99Ms}ms` }, { l: "Margin", v: `${safetyMarginMs}ms` },
          { l: "Recommended", v: `${recommendedTimeoutMs}ms` }, { l: "Budget", v: `${currentBudgetMs}ms` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
