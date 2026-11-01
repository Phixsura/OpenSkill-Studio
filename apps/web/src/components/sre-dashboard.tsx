"use client";

interface SreDashboardProps { burnRate: number; consumedPct: number;
  expectedPct: number; alert: string; healthy: boolean;
  toilPct: number; toilTarget: number; withinBudget: boolean; }

export function SreDashboard({ burnRate, consumedPct, expectedPct, alert, healthy, toilPct, toilTarget, withinBudget }: SreDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 SRE Dashboard</h3>
        <span className={`text-xs font-medium ${healthy ? "text-green-600" : "text-red-500"}`}>
          burn rate: {burnRate}x {alert !== "none" ? `· ${alert}` : ""}
        </span>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 border-b dark:border-gray-700">
        <div className="p-4">
          <div className="text-xs text-gray-400 mb-1">Error Budget</div>
          <div className="text-xl font-bold">{consumedPct}%</div>
          <div className="text-[10px] text-gray-400">consumed (expected {expectedPct}%)</div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full mt-2">
            <div className={`h-full rounded-full ${consumedPct > expectedPct * 1.5 ? "bg-red-500" : "bg-green-500"}`}
              style={{ width: `${Math.min(consumedPct, 100)}%` }} />
          </div>
        </div>
        <div className="p-4">
          <div className="text-xs text-gray-400 mb-1">Toil Budget</div>
          <div className="text-xl font-bold">{toilPct}%</div>
          <div className="text-[10px] text-gray-400">target &lt; {toilTarget}%</div>
          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full mt-2">
            <div className={`h-full rounded-full ${withinBudget ? "bg-green-500" : "bg-red-500"}`}
              style={{ width: `${Math.min(toilPct, 100)}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}
