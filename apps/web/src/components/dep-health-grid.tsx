"use client";

interface DepStatus { name: string; healthy: boolean; degraded: boolean; latencyMs: number; critical: boolean; }
interface DepHealthGridProps { dependencies: DepStatus[]; overall: string; }

const OVERALL_STYLE: Record<string, string> = {
  healthy: "text-green-600", degraded: "text-yellow-600", critical: "text-red-600",
};

export function DepHealthGrid({ dependencies, overall }: DepHealthGridProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Dependency Health</h3>
        <span className={`text-xs font-bold uppercase ${OVERALL_STYLE[overall] ?? ""}`}>{overall}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 p-4">
        {dependencies.map(d => (
          <div key={d.name} className={`rounded-lg p-2 text-xs border ${
            !d.healthy ? "border-red-300 bg-red-50 dark:bg-red-950" :
            d.degraded ? "border-yellow-300 bg-yellow-50 dark:bg-yellow-950" :
            "border-green-300 bg-green-50 dark:bg-green-950"}`}>
            <div className="flex items-center justify-between">
              <span className="font-semibold">{d.name}</span>
              {d.critical && <span className="text-red-500 text-[10px]">CRIT</span>}
            </div>
            <div className="text-gray-500 mt-0.5">{d.latencyMs}ms</div>
          </div>
        ))}
      </div>
    </div>
  );
}
