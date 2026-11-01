"use client";

interface CostTagViewProps { byCostCenter: Record<string, number>; untaggedCost: number;
  totalCost: number; taggedPct: number; }

export function CostTagView({ byCostCenter, untaggedCost, totalCost, taggedPct }: CostTagViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Cost Allocation</h3>
        <span className="text-xs text-gray-400">${totalCost.toLocaleString()} · {taggedPct}% tagged</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(byCostCenter).map(([cc, cost]) => (
          <div key={cc} className="flex justify-between px-4 py-2 text-xs">
            <span>{cc}</span><span className="font-mono">${cost.toLocaleString()}</span>
          </div>
        ))}
        {untaggedCost > 0 && (
          <div className="flex justify-between px-4 py-2 text-xs text-yellow-600">
            <span>⚠ Untagged</span><span className="font-mono">${untaggedCost}</span>
          </div>
        )}
      </div>
    </div>
  );
}
