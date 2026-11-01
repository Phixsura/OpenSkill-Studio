"use client";

interface Projection { month: number; usage: number; pctOfCapacity: number; }
interface CapacityPlannerWidgetProps { current: number; growthRate: number;
  projections: Projection[]; monthsToLimit: number | null; needsExpansion: boolean;
  recommendation: { action: string; urgency: string; recommendedCapacity: number }; }

export function CapacityPlannerWidget({ current, growthRate, projections, monthsToLimit, needsExpansion, recommendation }: CapacityPlannerWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📐 Capacity Planner</h3>
        <span className={`text-xs font-medium ${needsExpansion ? "text-red-500" : "text-green-600"}`}>
          {needsExpansion ? `⚠ Limit in ${monthsToLimit}mo` : "✅ Sufficient"}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{current}%</div>
          <div className="text-[10px] text-gray-400">Current</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{growthRate}%</div>
          <div className="text-[10px] text-gray-400">Growth/mo</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className={`text-lg font-bold ${recommendation.urgency === "high" ? "text-red-600" : ""}`}>{recommendation.action}</div>
          <div className="text-[10px] text-gray-400">{recommendation.urgency}</div>
        </div>
      </div>
      <div className="p-3 flex gap-1">
        {projections.slice(0, 6).map(p => (
          <div key={p.month} className="flex-1 text-center">
            <div className="text-[10px] text-gray-400">M{p.month}</div>
            <div className={`text-xs font-mono ${p.pctOfCapacity >= 100 ? "text-red-500 font-bold" : ""}`}>{p.pctOfCapacity}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}
