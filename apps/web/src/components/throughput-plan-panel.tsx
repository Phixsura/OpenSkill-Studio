"use client";
interface MonthPlan { month: number; rps: number; instances: number; }
interface ThroughputPlanPanelProps { targetRps: number; instancesNeeded: number;
  headroomPct: number; growthPlan: MonthPlan[]; }
export function ThroughputPlanPanel({ targetRps, instancesNeeded, headroomPct, growthPlan }: ThroughputPlanPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Throughput Plan</h3>
        <span className="text-xs text-gray-400">{targetRps.toLocaleString()} rps target · {instancesNeeded} instances · {headroomPct}% headroom</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {growthPlan.map(p => (
          <div key={p.month} className="flex justify-between px-4 py-1 text-xs">
            <span className="text-gray-400">Month {p.month}</span>
            <span>{p.rps.toLocaleString()} rps · {p.instances} instances</span>
          </div>
        ))}
      </div>
    </div>
  );
}
