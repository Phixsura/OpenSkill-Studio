"use client";

interface PoolStatus { pool: string; capacity: number; used: number; available: number;
  utilizationPct: number; owners: number; }
interface ResourcePoolWidgetProps { pools: PoolStatus[]; }

export function ResourcePoolWidget({ pools }: ResourcePoolWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏊 Resource Pools</h3>
        <span className="text-xs text-gray-400">{pools.length} pools</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {pools.map(p => (
          <div key={p.pool} className="px-4 py-2">
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold">{p.pool}</span>
              <span className="text-gray-400">{p.used}/{p.capacity} ({p.utilizationPct}%) · {p.owners} owners</span>
            </div>
            <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className={`h-full rounded-full ${p.utilizationPct > 90 ? "bg-red-500" : p.utilizationPct > 70 ? "bg-yellow-500" : "bg-green-500"}`}
                style={{ width: `${Math.min(p.utilizationPct, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
