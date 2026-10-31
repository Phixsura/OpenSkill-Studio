"use client";

interface Recommendation { name: string; action: string; savings: number;
  cpuAvgPct: number; memAvgPct: number; monthlyCost: number; }
interface RightsizeAdvisorProps { recommendations: Recommendation[];
  totalSavings: string; count: number; }

export function RightsizeAdvisor({ recommendations, totalSavings, count }: RightsizeAdvisorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📐 Rightsizing Advisor</h3>
        <div className="text-right">
          <div className="text-sm font-bold text-green-600">Save {totalSavings}</div>
          <div className="text-[10px] text-gray-400">{count} recommendations</div>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {recommendations.map(r => (
          <div key={r.name} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-mono">{r.name}</span>
              <div className="text-[10px] text-gray-400">CPU {r.cpuAvgPct}% · Mem {r.memAvgPct}% · ${r.monthlyCost}/mo</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-green-600">-${r.savings}/mo</div>
              <div className="text-[10px] text-gray-400">{r.action.replaceAll("_", " ")}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
