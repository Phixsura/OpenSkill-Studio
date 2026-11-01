"use client";

interface SavingsOpp { resource: string; type: string; utilizationPct: number;
  monthlyCost: number; potentialSavings: number; recommendation: string; }
interface InfraCostOptDashProps { totalMonthlyCost: number; potentialSavings: number;
  savingsPct: number; opportunities: SavingsOpp[]; }

export function InfraCostOptDash({ totalMonthlyCost, potentialSavings, savingsPct, opportunities }: InfraCostOptDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💸 Cost Optimizer</h3>
        <span className="text-xs text-green-600 font-bold">Save ${potentialSavings.toLocaleString()}/mo ({savingsPct}%)</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Monthly Cost</div><div className="font-bold text-lg">${totalMonthlyCost.toLocaleString()}</div></div>
        <div><div className="text-gray-400">Potential Savings</div><div className="font-bold text-lg text-green-600">${potentialSavings.toLocaleString()}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {opportunities.map(o => (
          <div key={o.resource} className="px-4 py-2 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-semibold">{o.resource} <span className="text-gray-400">({o.type})</span></span>
              <span className="text-green-600">-${o.potentialSavings}/mo</span>
            </div>
            <div className="text-gray-400">{o.utilizationPct}% util · {o.recommendation.replace(/_/g, " ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
