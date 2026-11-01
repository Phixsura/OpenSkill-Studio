"use client";
interface PoolInfo { name: string; active: number; maxSize: number; }
interface DbConnMonPanelProps { pools: PoolInfo[]; utilPct: number; healthy: boolean; saturated: string[]; }
export function DbConnMonPanel({ pools, utilPct, healthy, saturated }: DbConnMonPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔌 DB Connections</h3>
        <span className={`text-xs font-bold ${healthy ? "text-green-600" : "text-yellow-600"}`}>
          {utilPct}% util{saturated.length > 0 ? ` · ⚠ ${saturated.length} saturated` : ""}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pools.map(p => (
          <div key={p.name} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{p.name}</span>
            <span className={p.active >= p.maxSize * 0.9 ? "text-red-500 font-bold" : "text-gray-400"}>{p.active}/{p.maxSize}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
