"use client";

interface Recommendation { resource: string; type: string; reason: string; potential_savings: number; priority: string; }
interface CostOptimizerResultsProps { totalMonthlyCost: number; totalPotentialSavings: number;
  savingsPct: number; recommendations: Recommendation[]; onApply: (resource: string) => void; }

const priorityBadge: Record<string, string> = {
  high: "bg-red-100 text-red-700 dark:bg-red-900/30", medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  low: "bg-blue-100 text-blue-700 dark:bg-blue-900/30",
};

export function CostOptimizerResults({ totalMonthlyCost, totalPotentialSavings, savingsPct, recommendations, onApply }: CostOptimizerResultsProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Cost Optimization</h2>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-gray-50 p-3 text-center dark:bg-gray-800">
          <p className="text-lg font-bold">${totalMonthlyCost}/mo</p>
          <p className="text-xs text-gray-400">Current Cost</p>
        </div>
        <div className="rounded-lg bg-green-50 p-3 text-center dark:bg-green-900/10">
          <p className="text-lg font-bold text-green-600">-${totalPotentialSavings}</p>
          <p className="text-xs text-gray-400">Potential Savings</p>
        </div>
        <div className="rounded-lg bg-green-50 p-3 text-center dark:bg-green-900/10">
          <p className="text-lg font-bold text-green-600">{savingsPct}%</p>
          <p className="text-xs text-gray-400">Can Save</p>
        </div>
      </div>
      <div className="space-y-2">
        {recommendations.map((rec, i) => (
          <div key={i} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{rec.resource}</span>
                <span className={`rounded-full px-1.5 py-0.5 text-xs ${priorityBadge[rec.priority] ?? ""}`}>{rec.priority}</span>
              </div>
              <p className="text-xs text-gray-400">{rec.reason}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-green-600">-${rec.potential_savings}</span>
              <button onClick={() => onApply(rec.resource)} className="rounded bg-blue-600 px-2 py-1 text-xs text-white">Apply</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
