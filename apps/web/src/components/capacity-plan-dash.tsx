"use client";

interface Projection { month: number; projectedUsage: number; utilizationPct: number; }
interface CapacityPlanDashProps { current: number; capacity: number; growthRatePct: number;
  projections: Projection[]; exhaustionMonth: number | null; actionNeeded: boolean; }

export function CapacityPlanDash({ current, capacity, growthRatePct, projections, exhaustionMonth, actionNeeded }: CapacityPlanDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Capacity Planner</h3>
        <span className={`text-xs font-bold ${actionNeeded ? "text-red-500" : "text-green-600"}`}>
          {actionNeeded ? `⚠ Exhaust in ${exhaustionMonth}mo` : "✅ Sufficient"} · +{growthRatePct}%/mo
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><div className="text-gray-400">Current</div><div className="font-bold text-lg">{current}</div></div>
        <div><div className="text-gray-400">Capacity</div><div className="font-bold text-lg">{capacity}</div></div>
      </div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {projections.map(p => (
          <div key={p.month} className="flex items-center justify-between px-4 py-1 text-xs">
            <span className="text-gray-400">Month {p.month}</span>
            <span className={p.utilizationPct >= 100 ? "text-red-500 font-bold" : p.utilizationPct >= 80 ? "text-yellow-600" : "text-gray-400"}>
              {p.projectedUsage} ({p.utilizationPct}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
