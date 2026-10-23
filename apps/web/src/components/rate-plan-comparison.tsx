"use client";

interface PlanComparison { plan_name: string; cost: number; }
interface RatePlanComparisonProps { comparisons: PlanComparison[]; recommended: string | null; onSelect: (plan: string) => void; }

export function RatePlanComparison({ comparisons, recommended, onSelect }: RatePlanComparisonProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Plan Comparison</h2>
      <p className="text-sm text-gray-400">Based on your current usage</p>
      <div className="grid gap-3 sm:grid-cols-2">
        {comparisons.map(c => (
          <div key={c.plan_name} className={`rounded-lg border p-4 ${c.plan_name === recommended ? "border-green-500 bg-green-50 dark:bg-green-900/10" : "dark:border-gray-700"}`}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{c.plan_name}</span>
              {c.plan_name === recommended && <span className="text-xs text-green-600">✨ Best Value</span>}
            </div>
            <p className="mt-2 text-2xl font-bold">${c.cost.toFixed(2)}<span className="text-sm font-normal text-gray-400">/mo</span></p>
            <button onClick={() => onSelect(c.plan_name)}
              className={`mt-3 w-full rounded py-1.5 text-sm ${c.plan_name === recommended ? "bg-green-600 text-white" : "border text-gray-600 dark:border-gray-600 dark:text-gray-300"}`}>
              {c.plan_name === recommended ? "Select Plan" : "Choose"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
