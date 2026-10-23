"use client";

interface Pool { name: string; active: number; idle: number; max_size: number;
  utilization_pct: number; healthy: boolean; waiting: number; }
interface ConnectionPoolMonitorProps { pools: Pool[]; overallHealth: string; }

export function ConnectionPoolMonitor({ pools, overallHealth }: ConnectionPoolMonitorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Connection Pools</h2>
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${overallHealth === "healthy" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {overallHealth}
        </span>
      </div>
      {pools.map(p => (
        <div key={p.name} className={`rounded-lg border p-3 ${p.healthy ? "dark:border-gray-700" : "border-red-300 dark:border-red-700"}`}>
          <div className="flex items-center justify-between">
            <span className="font-medium">{p.name}</span>
            <span className="text-xs text-gray-400">{p.active}/{p.max_size} active</span>
          </div>
          <div className="mt-1.5 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className={`h-full rounded-full ${p.healthy ? "bg-blue-500" : "bg-red-500"}`}
              style={{ width: `${Math.min(p.utilization_pct, 100)}%` }} />
          </div>
          <div className="mt-1 flex justify-between text-xs text-gray-400">
            <span>{p.utilization_pct}% utilized</span>
            {p.waiting > 0 && <span className="text-red-500">{p.waiting} waiting</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
