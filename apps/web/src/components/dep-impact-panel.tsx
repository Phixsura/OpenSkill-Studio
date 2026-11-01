"use client";
interface ImpactInfo { service: string; blastRadius: number; impactPct: number; }
interface DepImpactPanelProps { impacts: ImpactInfo[]; totalServices: number; }
export function DepImpactPanel({ impacts, totalServices }: DepImpactPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">💥 Dependency Impact</h3>
        <span className="text-xs text-gray-400">{totalServices} services analyzed</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {impacts.map(i => (
          <div key={i.service} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className={`font-mono ${i.impactPct > 50 ? "text-red-600 font-bold" : ""}`}>{i.service}</span>
            <div className="flex items-center gap-2">
              <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                <div className={`h-full rounded-full ${i.impactPct > 50 ? "bg-red-500" : i.impactPct > 25 ? "bg-yellow-500" : "bg-green-500"}`}
                  style={{ width: `${i.impactPct}%` }} />
              </div>
              <span className="text-gray-400 w-16 text-right">{i.blastRadius} svcs ({i.impactPct}%)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
