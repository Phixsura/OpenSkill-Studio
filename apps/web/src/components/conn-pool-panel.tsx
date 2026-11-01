"use client";

interface PoolStats {
  target: string;
  active: number;
  idle: number;
  total: number;
  max: number;
}

export function ConnPoolPanel({ pools }: { pools: PoolStats[] }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🔌 Connection Pools</h2>
      <div className="space-y-2">
        {pools.map((p) => {
          const pct = Math.round((p.total / p.max) * 100);
          return (
            <div key={p.target} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <code className="text-sm font-semibold">{p.target}</code>
                <span className={`text-sm font-bold ${pct > 80 ? "text-red-600" : "text-green-600"}`}>{pct}%</span>
              </div>
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden mb-2">
                <div className="h-full flex">
                  <div className="bg-blue-500" style={{ width: `${(p.active / p.max) * 100}%` }} />
                  <div className="bg-green-400" style={{ width: `${(p.idle / p.max) * 100}%` }} />
                </div>
              </div>
              <div className="flex gap-3 text-xs text-gray-500">
                <span className="text-blue-600">● {p.active} active</span>
                <span className="text-green-600">● {p.idle} idle</span>
                <span>{p.total}/{p.max} total</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
