"use client";

interface WastedResource { name: string; usagePct: number; cost: number; wastedCost: number; action: string; }
interface ResOptimizerCardProps { wastedResources: WastedResource[];
  totalWasteCost: string; wasteCount: number; onOptimize: (name: string) => void; }

export function ResOptimizerCard({ wastedResources, totalWasteCost, wasteCount, onOptimize }: ResOptimizerCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💡 Resource Optimizer</h3>
        <div className="text-right">
          <div className="text-sm font-bold text-green-600">Save {totalWasteCost}</div>
          <div className="text-[10px] text-gray-400">{wasteCount} resources</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {wastedResources.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-mono">{r.name}</span>
              <div className="text-[10px] text-gray-400">{r.usagePct}% used · ${r.cost}/mo · save ${r.wastedCost}</div>
            </div>
            <button onClick={() => onOptimize(r.name)}
              className="px-2 py-1 text-xs bg-green-500 text-white rounded">{r.action === "terminate_or_downsize" ? "Remove" : "Resize"}</button>
          </div>
        ))}
      </div>
    </div>
  );
}
