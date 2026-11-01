"use client";

interface Projection { month: number; usage: number; pct: number; exceeded: boolean; }
interface CapacityPlannerChartProps { currentPct: number; capacity: number; unit: string;
  growthRatePct: number; exhaustionMonth: number | null; recommendation: string;
  projections: Projection[]; actionNeeded: boolean; }

export function CapacityPlannerChart({ currentPct, capacity, unit, growthRatePct,
  exhaustionMonth, recommendation, projections, actionNeeded }: CapacityPlannerChartProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📐 Capacity Planner</h3>
        {actionNeeded && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">⚠️ Action Needed</span>}
      </div>
      <div className="grid grid-cols-4 gap-3 text-center mb-4">
        <div><p className="text-lg font-bold">{currentPct}%</p><p className="text-xs text-gray-400">Current</p></div>
        <div><p className="text-lg font-bold">{capacity} {unit}</p><p className="text-xs text-gray-400">Capacity</p></div>
        <div><p className="text-lg font-bold">{growthRatePct}%</p><p className="text-xs text-gray-400">Growth/mo</p></div>
        <div><p className="text-lg font-bold">{exhaustionMonth ?? "—"}</p><p className="text-xs text-gray-400">Months Left</p></div>
      </div>
      <div className="flex items-end gap-0.5 h-24 mb-3">
        {projections.slice(0, 12).map(p => (
          <div key={p.month} className="flex-1 flex flex-col justify-end">
            <div className={`rounded-t ${p.exceeded ? "bg-red-400" : p.pct > 80 ? "bg-yellow-400" : "bg-blue-400"}`}
                 style={{ height: `${Math.min(p.pct, 100)}%` }} />
          </div>
        ))}
      </div>
      <div className={`p-3 rounded-lg text-xs ${actionNeeded ? "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400" : "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400"}`}>
        {recommendation}
      </div>
    </div>
  );
}
