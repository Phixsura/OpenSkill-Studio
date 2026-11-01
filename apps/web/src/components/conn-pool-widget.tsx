"use client";

interface PoolInfo { name: string; active: number; idle: number; maxSize: number;
  utilizationPct: number; waits: number; }
interface ConnPoolWidgetProps { pools: PoolInfo[]; }

export function ConnPoolWidget({ pools }: ConnPoolWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Connection Pools</h3>
        <span className="text-xs text-gray-400">{pools.length} pools</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pools.map(p => (
          <div key={p.name} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold">{p.name}</span>
              <span className="text-gray-400">{p.active}/{p.maxSize} active ({p.utilizationPct}%){p.waits > 0 ? ` · ${p.waits} waits` : ""}</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${p.utilizationPct > 90 ? "bg-red-500" : p.utilizationPct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${p.utilizationPct}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
