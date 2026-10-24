"use client";

interface Recommendation { name: string; type: string; monthlyCost: number;
  utilizationPct: number; suggestion: string; saving: number; }
interface CostOptimizationCardProps { totalCost: number; potentialSavings: number;
  savingsPct: number; recommendations: Recommendation[]; }

export function CostOptimizationCard({ totalCost, potentialSavings, savingsPct, recommendations }: CostOptimizationCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💡 Cost Optimization</h3>
        <div className="text-right">
          <div className="text-sm font-bold text-green-600">Save ${potentialSavings}/mo</div>
          <div className="text-[10px] text-gray-400">{savingsPct}% of ${totalCost}/mo</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {recommendations.map(r => (
          <div key={r.name} className="px-4 py-2.5">
            <div className="flex justify-between text-xs">
              <span className="font-medium">{r.name} <span className="text-gray-400">({r.type})</span></span>
              <span className="text-green-600">-${r.saving}/mo</span>
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              {r.utilizationPct}% utilized · ${r.monthlyCost}/mo · {r.suggestion.replaceAll("_", " ")}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
