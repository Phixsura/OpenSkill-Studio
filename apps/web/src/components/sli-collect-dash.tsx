"use client";

interface SliSummary { sli: string; count: number; avg: number; p99: number; goodPct: number; }
interface SliCollectDashProps { slis: SliSummary[]; }

export function SliCollectDash({ slis }: SliCollectDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📏 SLI Dashboard</h3>
        <span className="text-xs text-gray-400">{slis.length} indicators</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {slis.map(s => (
          <div key={s.sli} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{s.sli}</span>
            <div className="flex items-center gap-3 text-gray-400">
              <span>avg: {s.avg}</span>
              <span>p99: {s.p99}</span>
              <span className={s.goodPct >= 99 ? "text-green-600" : "text-yellow-600"}>{s.goodPct}% good</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
