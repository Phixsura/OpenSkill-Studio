"use client";
interface PoolInfo { service: string; destination: string; active: number; maxSize: number; utilPct: number; saturated: boolean; }
interface MeshConnPoolPanelProps { pools: PoolInfo[]; saturated: number; healthy: number; }
export function MeshConnPoolPanel({ pools, saturated, healthy }: MeshConnPoolPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 Mesh Conn Pools</h3>
        <span className={`text-xs ${saturated > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {healthy} healthy{saturated > 0 ? ` · ⚠ ${saturated} saturated` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pools.map(p => (
          <div key={`${p.service}→${p.destination}`} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-0.5">
              <span className="font-mono">{p.service}→{p.destination}</span>
              <span className={p.saturated ? "text-red-500 font-bold" : "text-gray-400"}>{p.active}/{p.maxSize} ({p.utilPct}%)</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${p.saturated ? "bg-red-500" : "bg-green-500"}`} style={{ width: `${p.utilPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
