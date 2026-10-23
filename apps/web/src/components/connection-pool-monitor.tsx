"use client";

interface PoolStats { maxSize: number; active: number; idle: number;
  utilizationDisplay: string; waits: number; health: string; }
interface ConnectionPoolMonitorProps { pools: { name: string; stats: PoolStats }[]; }

export function ConnectionPoolMonitor({ pools }: ConnectionPoolMonitorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔌 Connection Pools</h3>
      <div className="space-y-4">
        {pools.map(p => (
          <div key={p.name}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{p.name}</span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">{p.stats.utilizationDisplay}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  p.stats.health === "healthy" ? "bg-green-100 text-green-700" :
                  p.stats.health === "busy" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
                }`}>{p.stats.health}</span>
              </div>
            </div>
            <div className="flex h-4 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800">
              <div className="bg-blue-500 h-full" style={{ width: `${(p.stats.active / p.stats.maxSize) * 100}%` }}
                   title={`Active: ${p.stats.active}`} />
              <div className="bg-blue-200 dark:bg-blue-800 h-full" style={{ width: `${(p.stats.idle / p.stats.maxSize) * 100}%` }}
                   title={`Idle: ${p.stats.idle}`} />
            </div>
            <div className="flex gap-4 mt-1 text-xs text-gray-400">
              <span>Active: {p.stats.active}</span>
              <span>Idle: {p.stats.idle}</span>
              <span>Max: {p.stats.maxSize}</span>
              {p.stats.waits > 0 && <span className="text-red-500">{p.stats.waits} waits</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
