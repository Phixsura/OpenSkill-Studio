"use client";

interface Sli { name: string; ratioPct: number; objectivePct: number;
  meetingObjective: boolean; budgetConsumedPct: number; }
interface SliDashboardProps { slis: Sli[]; allMeeting: boolean; avgRatio: number; }

export function SliDashboard({ slis, allMeeting, avgRatio }: SliDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📏 Service Level Indicators</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">avg {avgRatio}%</span>
          <span className={allMeeting ? "text-green-600" : "text-red-500"}>
            {allMeeting ? "✅ All Met" : "⚠ Objectives Missed"}
          </span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {slis.map(s => (
          <div key={s.name} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{s.meetingObjective ? "🟢" : "🔴"} {s.name}</span>
              <span className="text-xs font-mono">
                {s.ratioPct}% / {s.objectivePct}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${s.budgetConsumedPct > 80 ? "bg-red-500" : s.budgetConsumedPct > 50 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(s.budgetConsumedPct, 100)}%` }} />
            </div>
            <div className="text-[10px] text-gray-400 mt-0.5">Error budget: {s.budgetConsumedPct}% consumed</div>
          </div>
        ))}
      </div>
    </div>
  );
}
