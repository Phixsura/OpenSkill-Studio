"use client";

interface PoolStats { active: number; idle: number; waiting: number; maxSize: number; utilizationPct: number; healthy: boolean; }
interface ConnectionPoolMonitorProps { stats: PoolStats; }

export function ConnectionPoolMonitor({ stats }: ConnectionPoolMonitorProps) {
  const color = stats.healthy ? "bg-green-500" : "bg-red-500";
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Connection Pool</h3>
        <div className="flex items-center gap-1.5">
          <span className={`h-2 w-2 rounded-full ${color}`} />
          <span className="text-xs text-gray-400">{stats.healthy ? "Healthy" : "Saturated"}</span>
        </div>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        <div><p className="text-lg font-bold text-blue-600">{stats.active}</p><p className="text-xs text-gray-400">Active</p></div>
        <div><p className="text-lg font-bold text-green-600">{stats.idle}</p><p className="text-xs text-gray-400">Idle</p></div>
        <div><p className="text-lg font-bold text-yellow-600">{stats.waiting}</p><p className="text-xs text-gray-400">Waiting</p></div>
        <div><p className="text-lg font-bold">{stats.maxSize}</p><p className="text-xs text-gray-400">Max</p></div>
      </div>
      <div className="mt-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full transition-all ${stats.utilizationPct > 80 ? "bg-red-500" : "bg-blue-500"}`}
          style={{ width: `${stats.utilizationPct}%` }} />
      </div>
      <p className="mt-1 text-center text-xs text-gray-400">{stats.utilizationPct}% utilized</p>
    </div>
  );
}
