"use client";

interface CostEntry { team?: string; service?: string; cost: number; pct: number; display: string; }
interface CostBreakdownChartProps { totalDisplay: string; byTeam: CostEntry[]; byService: CostEntry[]; }

const COLORS = ["bg-blue-500", "bg-green-500", "bg-yellow-500", "bg-purple-500", "bg-red-500", "bg-pink-500"];

export function CostBreakdownChart({ totalDisplay, byTeam, byService }: CostBreakdownChartProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💸 Cost Allocation</h3>
        <span className="text-lg font-bold">{totalDisplay}</span>
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">By Team</h4>
          {byTeam.map((t, i) => (
            <div key={t.team} className="mb-2">
              <div className="flex justify-between text-sm mb-1">
                <span className="capitalize">{t.team}</span>
                <span className="text-gray-500">{t.display} ({t.pct}%)</span>
              </div>
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full">
                <div className={`h-full rounded-full ${COLORS[i % COLORS.length]}`} style={{ width: `${t.pct}%` }} />
              </div>
            </div>
          ))}
        </div>
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">By Service</h4>
          {byService.map((s, i) => (
            <div key={s.service} className="mb-2">
              <div className="flex justify-between text-sm mb-1">
                <span className="capitalize">{s.service}</span>
                <span className="text-gray-500">{s.display} ({s.pct}%)</span>
              </div>
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full">
                <div className={`h-full rounded-full ${COLORS[(i + 2) % COLORS.length]}`} style={{ width: `${s.pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
