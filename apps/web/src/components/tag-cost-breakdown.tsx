"use client";

interface CostGroup { tag: string; cost: number; resources: number; pct: number; display: string; }
interface TagCostBreakdownProps { tagKey: string; totalDisplay: string;
  breakdown: CostGroup[]; untaggedCost: number; coveragePct: number; }

const COLORS = ["bg-blue-500", "bg-green-500", "bg-purple-500", "bg-yellow-500", "bg-red-500"];

export function TagCostBreakdown({ tagKey, totalDisplay, breakdown, untaggedCost, coveragePct }: TagCostBreakdownProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">💰 Cost by {tagKey}</h3>
        <div className="text-right">
          <p className="text-lg font-bold">{totalDisplay}</p>
          <p className="text-xs text-gray-400">{coveragePct}% tagged</p>
        </div>
      </div>
      <div className="flex h-4 rounded-full overflow-hidden mb-4">
        {breakdown.map((g, i) => (
          <div key={g.tag} className={COLORS[i % COLORS.length]} style={{ width: `${g.pct}%` }} title={`${g.tag}: ${g.pct}%`} />
        ))}
        {untaggedCost > 0 && <div className="bg-gray-300 dark:bg-gray-600" style={{ width: `${100 - coveragePct}%` }} />}
      </div>
      <div className="space-y-1">
        {breakdown.map((g, i) => (
          <div key={g.tag} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${COLORS[i % COLORS.length]}`} />
              <span className="capitalize">{g.tag}</span>
              <span className="text-xs text-gray-400">{g.resources} resources</span>
            </div>
            <span>{g.display} ({g.pct}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
