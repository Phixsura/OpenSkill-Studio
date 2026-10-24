"use client";
interface WastefulResource { name: string; cost: number; utilization: number; potentialSavings: number; }
interface CostEfficiencyPanelProps { score: number; avgUtilization: number; totalCost: number;
  potentialSavings: number; wasteful: WastefulResource[]; }
export function CostEfficiencyPanel({ score, avgUtilization, totalCost, potentialSavings, wasteful }: CostEfficiencyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💡 Cost Efficiency</h3>
        <span className={`text-xs font-bold ${score >= 70 ? "text-green-600" : "text-yellow-600"}`}>
          Score: {score} · avg {avgUtilization}% util · save ${potentialSavings.toLocaleString()}
        </span>
      </div>
      {wasteful.length > 0 && (
        <div className="divide-y dark:divide-gray-700">
          {wasteful.map(w => (
            <div key={w.name} className="flex justify-between px-4 py-1.5 text-xs">
              <span className="font-mono text-yellow-600">{w.name} ({w.utilization}% util)</span>
              <span className="text-green-600">save ${w.potentialSavings}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
