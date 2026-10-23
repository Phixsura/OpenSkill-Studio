"use client";

interface SliData { metric: string; sli: number; sliDisplay: string;
  sloTarget: number; met: boolean; errorBudgetPct: number; status: string; }
interface SliDashboardProps { slis: SliData[]; compositeDisplay: string; allMet: boolean; }

export function SliDashboard({ slis, compositeDisplay, allMet }: SliDashboardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📏 Service Level Indicators</h3>
        <div className="flex gap-2">
          <span className="text-sm font-bold">{compositeDisplay}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${allMet ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {allMet ? "✅ All SLOs met" : "⚠️ SLO breach"}
          </span>
        </div>
      </div>
      <div className="space-y-3">
        {slis.map(s => (
          <div key={s.metric}>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium capitalize">{s.metric}</span>
              <span className={s.met ? "text-green-600" : "text-red-600"}>{s.sliDisplay} / {s.sloTarget}%</span>
            </div>
            <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${s.met ? "bg-green-500" : "bg-red-500"}`}
                   style={{ width: `${Math.min(s.sli, 100)}%` }} />
            </div>
            <p className="text-xs text-gray-400 mt-0.5">Error budget: {s.errorBudgetPct}% consumed</p>
          </div>
        ))}
      </div>
    </div>
  );
}
