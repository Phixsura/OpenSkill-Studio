"use client";

interface ImpactRank { service: string; blastRadius: number; impactPct: number; }
interface ImpactAnalysisCardProps { rankings: ImpactRank[]; totalServices: number; }

export function ImpactAnalysisCard({ rankings, totalServices }: ImpactAnalysisCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💥 Impact Analysis</h3>
        <span className="text-xs text-gray-400">{totalServices} services</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {rankings.map((r, i) => (
          <div key={r.service} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${i === 0 ? "bg-red-500 text-white" : "bg-gray-200 dark:bg-gray-700 text-gray-500"}`}>{i + 1}</span>
              <span className="text-sm font-medium">{r.service}</span>
            </div>
            <div className="flex gap-2 text-xs text-gray-400">
              <span className="font-bold text-red-500">{r.blastRadius}</span>
              <span>affected ({r.impactPct}%)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
